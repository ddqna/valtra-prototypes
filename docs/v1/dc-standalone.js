/*
 * dc-standalone.js — a tiny runtime that renders the prototype screens
 * (Claude Design ".dc.html" format) in any browser, without the canvas.
 *
 * Supported template syntax (the subset these prototypes use):
 *   {{ path }}               dotted lookup into renderVals() / loop scope
 *   attr="{{ path }}"        raw value (functions for onClick etc., booleans)
 *   attr="a {{ p }} b"       interpolated string
 *   <sc-if value="{{ x }}">  conditional block
 *   <sc-for list="{{ xs }}" as="item">  repeat block ($index in scope)
 *   class Component extends DCLogic { renderVals() {...} }  with state/setState
 */
(function () {
  'use strict';

  var HOLE = /\{\{\s*([^}]+?)\s*\}\}/g;
  var WHOLE = /^\s*\{\{\s*([^}]+?)\s*\}\}\s*$/;

  function lookup(path, scope) {
    path = path.trim();
    if (path === 'true') return true;
    if (path === 'false') return false;
    if (path === 'null') return null;
    if (/^-?\d+(\.\d+)?$/.test(path)) return Number(path);
    if (/^(['"]).*\1$/.test(path)) return path.slice(1, -1);
    var parts = path.split('.');
    var cur = scope;
    for (var i = 0; i < parts.length; i++) {
      if (cur == null) return undefined;
      cur = cur[parts[i]];
    }
    return cur;
  }

  function interpolate(str, scope) {
    return str.replace(HOLE, function (_, p) {
      var v = lookup(p, scope);
      return v == null ? '' : String(v);
    });
  }

  // HTML lowercases attribute names: map JSX-style event names back.
  function eventName(attr) {
    return attr.slice(2).toLowerCase();
  }

  function processChildren(parent, scope, out) {
    var kids = Array.prototype.slice.call(parent.childNodes);
    for (var i = 0; i < kids.length; i++) processNode(kids[i], scope, out);
  }

  function processNode(node, scope, out) {
    if (node.nodeType === 3) { // text
      out.appendChild(document.createTextNode(interpolate(node.nodeValue, scope)));
      return;
    }
    if (node.nodeType !== 1) return; // drop comments
    var tag = node.tagName.toLowerCase();

    if (tag === 'sc-if') {
      var m = WHOLE.exec(node.getAttribute('value') || '');
      if (m && lookup(m[1], scope)) processChildren(node, scope, out);
      return;
    }
    if (tag === 'sc-for') {
      var lm = WHOLE.exec(node.getAttribute('list') || '');
      var list = lm ? lookup(lm[1], scope) : null;
      var as = node.getAttribute('as') || 'item';
      (list || []).forEach(function (item, idx) {
        var s = Object.create(scope);
        s[as] = item;
        s.$index = idx;
        processChildren(node, s, out);
      });
      return;
    }
    if (tag === 'helmet') return;

    var el = node.namespaceURI === 'http://www.w3.org/1999/xhtml'
      ? document.createElement(node.localName)
      : document.createElementNS(node.namespaceURI, node.localName);
    for (var a = 0; a < node.attributes.length; a++) {
      var attr = node.attributes[a];
      var name = attr.name, value = attr.value;
      if (name.indexOf('hint-') === 0) continue;
      var whole = WHOLE.exec(value);
      if (whole) {
        var v = lookup(whole[1], scope);
        if (/^on/i.test(name)) {
          if (typeof v === 'function') el.addEventListener(eventName(name), v);
          continue;
        }
        if (v === false || v == null) continue;
        el.setAttribute(name, v === true ? '' : String(v));
      } else if (value.indexOf('{{') !== -1) {
        el.setAttribute(name, interpolate(value, scope));
      } else {
        el.setAttribute(name, value);
      }
    }
    processChildren(node, scope, el);
    out.appendChild(el);
  }

  function DCLogic(props) {
    this.props = props || {};
    this.state = {};
  }
  DCLogic.prototype.setState = function (patch) {
    if (typeof patch === 'function') patch = patch(this.state, this.props);
    this.state = Object.assign({}, this.state, patch);
    if (this.__render) this.__render();
  };
  DCLogic.prototype.forceUpdate = function () { if (this.__render) this.__render(); };
  DCLogic.prototype.renderVals = function () { return {}; };

  function fit(stage, w, h) {
    var s = Math.min(window.innerWidth / w, window.innerHeight / h);
    stage.style.transform = 'translate(-50%, -50%) scale(' + s + ')';
  }

  function boot() {
    var host = document.querySelector('x-dc');
    var scriptEl = document.querySelector('script[type="text/x-dc"]');
    if (!host || !scriptEl) return;

    // Move <helmet> contents (fonts, styles) into <head>.
    var helmet = host.querySelector('helmet');
    if (helmet) {
      Array.prototype.slice.call(helmet.children).forEach(function (n) { document.head.appendChild(n); });
    }

    // Keep the authored markup as an inert template.
    var tpl = document.createElement('template');
    while (host.firstChild) tpl.content.appendChild(host.firstChild);
    host.remove();

    var Component = new Function('DCLogic', scriptEl.textContent + '\n;return Component;')(DCLogic);
    var preview = {};
    try { preview = (JSON.parse(scriptEl.getAttribute('data-props') || '{}').$preview) || {}; } catch (e) {}
    var W = preview.width || 1280, H = preview.height || 800;

    var stage = document.createElement('div');
    stage.id = 'dc-stage';
    stage.style.cssText = 'position:fixed;left:50%;top:50%;width:' + W + 'px;height:' + H + 'px;transform-origin:center center';
    document.body.appendChild(stage);

    var inst = new Component({});
    inst.__render = function () {
      var vals = inst.renderVals() || {};
      var frag = document.createDocumentFragment();
      processChildren(tpl.content, vals, frag);
      stage.replaceChildren(frag);
    };
    inst.__render();
    if (inst.componentDidMount) inst.componentDidMount();

    fit(stage, W, H);
    window.addEventListener('resize', function () { fit(stage, W, H); });
  }

  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', boot);
  else boot();
})();
