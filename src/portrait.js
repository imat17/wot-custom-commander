(function () {
  'use strict';
  if (window.__commanderFriend) return;
  window.__commanderFriend = true;
  var dirty = false;
  var saved = new Map();
  function readState() {
    if (!window.subViews) return null;
    var ids = window.subViews.ids();
    for (var id of ids) {
      var view = window.subViews.get(id);
      var raw = view && view.model && view.model.commanderFriendJson;
      if (raw && typeof raw === 'object' && 'value' in raw) raw = raw.value;
      if (typeof raw === 'string') {
        try { return JSON.parse(raw); } catch (e) { return null; }
      }
    }
    return null;
  }
  function restore(node, old) {
    if (node.style.getPropertyValue('background-image') === old.applied) {
      node.style.setProperty('background-image', old.image, old.priority);
    }
    node.removeAttribute('data-commander-friend');
  }
  function render() {
    dirty = false;
    var state = readState();
    var targets = new Set();
    var url = state && state.portrait;
    if (url && /^coui:\/\/gui\/maps\/icons\/commander_friend\/(?:(demo|friend)\.png|profiles\/papacito\/portrait\.jpg)$/.test(url)) {
      document.querySelectorAll('[class*="CrewWidget_"]').forEach(function (root) {
        var slots = Array.from(root.querySelectorAll('div')).filter(function (node) {
          return /(?:^|\s)Slot_[0-9a-f]+(?:\s|$)/.test(node.className);
        });
        (state.slots || []).forEach(function (index) {
          var slot = slots[index];
          var picture = slot && slot.querySelector('[class*="Tankman_content_"]');
          if (!picture) return;
          targets.add(picture);
          var value = 'url("' + url + '")';
          var old = saved.get(picture);
          if (!old || picture.style.getPropertyValue('background-image') !== old.applied) saved.set(picture, {
            image: picture.style.getPropertyValue('background-image'),
            priority: picture.style.getPropertyPriority('background-image'),
            applied: value
          });
          saved.get(picture).applied = value;
          if (picture.style.getPropertyValue('background-image') !== value) {
            picture.style.setProperty('background-image', value, 'important');
          }
          picture.setAttribute('data-commander-friend', 'true');
        });
      });
    }
    saved.forEach(function (old, node) {
      if (!targets.has(node)) { restore(node, old); saved.delete(node); }
    });
  }
  function schedule() {
    if (!dirty) { dirty = true; window.requestAnimationFrame(render); }
  }
  engine.whenReady.then(function () {
    var observer = new MutationObserver(schedule);
    observer.observe(document.body, {childList: true, subtree: true});
    engine.on('subViews.onAdded', schedule);
    var timer = window.setInterval(schedule, 500);
    window.addEventListener('beforeunload', function () {
      observer.disconnect(); window.clearInterval(timer);
      saved.forEach(function (old, node) { restore(node, old); });
    });
    schedule();
  });
})();
