/**
 * NDR Template-Tag Inserter
 *
 * Injects an "Insert NDR Tag" button above every CKEditor5 field that carries
 * the data-ndr-ckeditor attribute.  Clicking it opens a Bootstrap modal; on
 * confirm the generated tag is inserted at the cursor (or wraps the selection
 * for block/cell/code tags).
 */
(function () {
    'use strict';

    // ID of the editor currently targeted by the modal
    var _activeEditorId = null;

    // ------------------------------------------------------------------ //
    // Button injection                                                     //
    // ------------------------------------------------------------------ //

    function injectButton(editorId) {
        var editorEl = document.getElementById(editorId);
        if (!editorEl) return;

        var parent = editorEl.parentElement;
        if (!parent) return;

        // Avoid double-injection
        if (parent.querySelector('.ndr-tag-btn[data-editor-id="' + editorId + '"]')) return;

        var ckEditor = parent.querySelector('.ck-editor');
        if (!ckEditor) return;

        var btn = document.createElement('button');
        btn.type = 'button';
        btn.className = 'btn btn-sm btn-outline-secondary mb-1 ndr-tag-btn';
        btn.dataset.editorId = editorId;
        btn.innerHTML = '<i class="fa-solid fa-code"></i> Insert NDR Tag';
        btn.addEventListener('click', function () {
            openModal(editorId);
        });

        parent.insertBefore(btn, ckEditor);
    }

    function setupEditor(editorId) {
        if (window.editors && window.editors[editorId]) {
            injectButton(editorId);
        } else if (window.ckeditorRegisterCallback) {
            window.ckeditorRegisterCallback(editorId, function () {
                injectButton(editorId);
            });
        }
    }

    // ------------------------------------------------------------------ //
    // Modal                                                                //
    // ------------------------------------------------------------------ //

    function openModal(editorId) {
        _activeEditorId = editorId;
        resetModal();
        updatePreview();
        var modalEl = document.getElementById('ndrTagModal');
        if (!modalEl) return;
        var modal = bootstrap.Modal.getOrCreateInstance(modalEl);
        modal.show();
    }

    function resetModal() {
        // Blocks tab defaults
        document.getElementById('ndrBlockTypeBlock').checked = true;
        var titleEl = document.getElementById('ndrBlockTitle');
        if (titleEl) titleEl.value = '';
        var collEl = document.getElementById('ndrBlockCollapsible');
        if (collEl) collEl.checked = false;
        var topEl = document.getElementById('ndrBlockBackToTop');
        if (topEl) topEl.checked = false;
        var cellW = document.getElementById('ndrCellWidth');
        if (cellW) cellW.value = '';
        var codeLang = document.getElementById('ndrCodeLang');
        if (codeLang) codeLang.value = '';
        showBlockSubOptions('block');

        // Elements tab
        var elSelect = document.getElementById('ndrElement');
        if (elSelect) elSelect.value = '';

        // Links tab – internal
        var pageSelect = document.getElementById('ndrLinkPage');
        if (pageSelect) pageSelect.value = '';
        var pageLabel = document.getElementById('ndrPageLabel');
        if (pageLabel) pageLabel.value = '';
        resetLinkStyle('ndrPage');

        // Links tab – external
        var extUrl = document.getElementById('ndrExtUrl');
        if (extUrl) extUrl.value = '';
        var extLabel = document.getElementById('ndrExtLabel');
        if (extLabel) extLabel.value = '';
        resetLinkStyle('ndrExt');

        // Links tab – file
        var fileSelect = document.getElementById('ndrFileUpload');
        if (fileSelect) fileSelect.value = '';
        var fileLabel = document.getElementById('ndrFileLabel');
        if (fileLabel) fileLabel.value = '';

        // Generated tab
        var tocRadio = document.getElementById('ndrGenToc');
        if (tocRadio) tocRadio.checked = true;
        var settingPicker = document.getElementById('ndrSettingPicker');
        if (settingPicker) settingPicker.style.display = 'none';
        var settingSelect = document.getElementById('ndrSetting');
        if (settingSelect) settingSelect.value = '';

        // Reset to first main tab
        var firstTab = document.getElementById('ndr-tab-blocks');
        if (firstTab) {
            bootstrap.Tab.getOrCreateInstance(firstTab).show();
        }
    }

    function resetLinkStyle(prefix) {
        var linkRadio = document.getElementById(prefix + 'StyleLink');
        if (linkRadio) linkRadio.checked = true;
        var btnOpts = document.querySelector('.' + prefix + '-btn-options');
        if (btnOpts) btnOpts.style.display = 'none';
        var colorSel = document.getElementById(prefix + 'Color');
        if (colorSel) colorSel.value = 'primary';
        var normalSize = document.getElementById(prefix + 'SizeNormal');
        if (normalSize) normalSize.checked = true;
    }

    // ------------------------------------------------------------------ //
    // Tag builder                                                          //
    // ------------------------------------------------------------------ //

    function buildTag() {
        var activeTab = document.querySelector('#ndrTagTabs .nav-link.active');
        if (!activeTab) return null;
        var target = activeTab.dataset.bsTarget;

        if (target === '#ndrTabBlocks')    return buildBlockTag();
        if (target === '#ndrTabElements')  return buildElementTag();
        if (target === '#ndrTabLinks')     return buildLinkTag();
        if (target === '#ndrTabGenerated') return buildGeneratedTag();
        return null;
    }

    /** Returns {wrap:true, start, end} or {wrap:false, tag} */
    function buildBlockTag() {
        var type = document.querySelector('input[name="ndrBlockType"]:checked');
        if (!type) return null;

        if (type.value === 'block') {
            var title = (document.getElementById('ndrBlockTitle').value || '').trim();
            var collapsible = document.getElementById('ndrBlockCollapsible').checked;
            var backToTop  = document.getElementById('ndrBlockBackToTop').checked;

            var parts = [];
            if (title)      parts.push('title=' + title);
            if (collapsible) parts.push('collapsible=true');
            if (backToTop)   parts.push('back_to_top=true');

            var startTag = parts.length
                ? '[[start_block:' + parts.join(',') + ']]'
                : '[[start_block]]';
            return { wrap: true, start: startTag, end: '[[end_block]]' };
        }

        if (type.value === 'cell') {
            var width = (document.getElementById('ndrCellWidth').value || '').trim();
            var startTag = width ? '[[start_cell=' + width + ']]' : '[[start_cell]]';
            return { wrap: true, start: startTag, end: '[[end_cell]]' };
        }

        if (type.value === 'code') {
            var lang = document.getElementById('ndrCodeLang').value;
            var startTag = lang ? '[[start_code=' + lang + ']]' : '[[start_code]]';
            return { wrap: true, start: startTag, end: '[[end_code]]' };
        }

        return null;
    }

    function buildElementTag() {
        var el = document.getElementById('ndrElement');
        if (!el || !el.value) return null;
        return { wrap: false, tag: '[[element|' + el.value + ']]' };
    }

    function buildLinkTag() {
        var activeLink = document.querySelector('#ndrLinkTypeTabs .nav-link.active');
        if (!activeLink) return null;
        var target = activeLink.dataset.bsTarget;

        if (target === '#ndrLinkInternal') {
            var page = document.getElementById('ndrLinkPage');
            if (!page || !page.value) return null;
            var label = (document.getElementById('ndrPageLabel').value || '').trim();
            var tag = buildLinkStyleTag('page', 'ndrPage', page.value, label);
            return { wrap: false, tag: tag };
        }

        if (target === '#ndrLinkExternal') {
            var url = (document.getElementById('ndrExtUrl').value || '').trim();
            if (!url) return null;
            var label = (document.getElementById('ndrExtLabel').value || '').trim();
            if (!label) return null;
            var tag = buildLinkStyleTag('link', 'ndrExt', url, label);
            return { wrap: false, tag: tag };
        }

        if (target === '#ndrLinkFile') {
            var file = document.getElementById('ndrFileUpload');
            if (!file || !file.value) return null;
            var label = (document.getElementById('ndrFileLabel').value || '').trim();
            return {
                wrap: false,
                tag: label ? '[[file|' + file.value + '|' + label + ']]'
                           : '[[file|' + file.value + ']]'
            };
        }

        return null;
    }

    /** Build [[page-btn-primary-sm|id|Label]] or [[link|url|Label]] etc. */
    function buildLinkStyleTag(type, prefix, identifier, label) {
        var isBtn = document.getElementById(prefix + 'StyleBtn').checked;

        if (isBtn) {
            var color = document.getElementById(prefix + 'Color').value || 'primary';
            var size  = document.querySelector('input[name="' + prefix + 'Size"]:checked');
            var sizeVal = (size && size.value) ? size.value : '';

            var tagName = type + '-btn-' + color + (sizeVal ? '-' + sizeVal : '');
            return label
                ? '[[' + tagName + '|' + identifier + '|' + label + ']]'
                : '[[' + tagName + '|' + identifier + ']]';
        } else {
            return label
                ? '[[' + type + '|' + identifier + '|' + label + ']]'
                : '[[' + type + '|' + identifier + ']]';
        }
    }

    function buildGeneratedTag() {
        var type = document.querySelector('input[name="ndrGenType"]:checked');
        if (!type) return null;

        if (type.value === 'toc') {
            return { wrap: false, tag: '[[toc]]' };
        }

        if (type.value === 'setting') {
            var setting = document.getElementById('ndrSetting');
            if (!setting || !setting.value) return null;
            return { wrap: false, tag: '[[setting|' + setting.value + ']]' };
        }

        return null;
    }

    // ------------------------------------------------------------------ //
    // Live preview                                                         //
    // ------------------------------------------------------------------ //

    function updatePreview() {
        var preview = document.getElementById('ndrTagPreview');
        if (!preview) return;

        var tagInfo = buildTag();
        if (!tagInfo) {
            preview.textContent = '';
            return;
        }

        if (tagInfo.wrap) {
            preview.textContent = tagInfo.start + '  …  ' + tagInfo.end;
        } else {
            preview.textContent = tagInfo.tag;
        }
    }

    // ------------------------------------------------------------------ //
    // Editor insertion                                                     //
    // ------------------------------------------------------------------ //

    function insertIntoEditor(editorId, tagInfo) {
        var editor = window.editors && window.editors[editorId];
        if (!editor) return;

        var model     = editor.model;
        var selection = model.document.selection;

        model.change(function (writer) {
            if (tagInfo.wrap) {
                if (!selection.isCollapsed) {
                    // Wrap the selection: insert end first (preserves start position)
                    var range = selection.getFirstRange();
                    writer.insertText('\n' + tagInfo.end, range.end);
                    writer.insertText(tagInfo.start + '\n', range.start);
                } else {
                    var pos = selection.getFirstPosition();
                    writer.insertText(tagInfo.start + '\n\n' + tagInfo.end, pos);
                }
            } else {
                // Replace selection (or insert at cursor) with single tag
                if (!selection.isCollapsed) {
                    var range = selection.getFirstRange();
                    writer.remove(range);
                }
                var pos = selection.getFirstPosition();
                writer.insertText(tagInfo.tag, pos);
            }
        });
    }

    // ------------------------------------------------------------------ //
    // Block sub-option visibility                                          //
    // ------------------------------------------------------------------ //

    function showBlockSubOptions(type) {
        document.getElementById('ndrBlockOptions').style.display = (type === 'block') ? '' : 'none';
        document.getElementById('ndrCellOptions').style.display  = (type === 'cell')  ? '' : 'none';
        document.getElementById('ndrCodeOptions').style.display  = (type === 'code')  ? '' : 'none';
    }

    // ------------------------------------------------------------------ //
    // Event wiring                                                         //
    // ------------------------------------------------------------------ //

    document.addEventListener('DOMContentLoaded', function () {

        // --- find and set up all NDR CKEditor fields ---
        document.querySelectorAll('[data-ndr-ckeditor]').forEach(function (el) {
            setupEditor(el.id);
        });

        // --- block type toggle ---
        document.querySelectorAll('input[name="ndrBlockType"]').forEach(function (radio) {
            radio.addEventListener('change', function () {
                showBlockSubOptions(this.value);
                updatePreview();
            });
        });

        // --- preset width buttons ---
        document.querySelectorAll('.ndr-preset').forEach(function (btn) {
            btn.addEventListener('click', function () {
                var target = document.getElementById(this.dataset.target);
                if (target) {
                    target.value = this.dataset.value;
                    updatePreview();
                }
            });
        });

        // --- link style toggle (show/hide button options) ---
        document.querySelectorAll('.ndr-style-radio').forEach(function (radio) {
            radio.addEventListener('change', function () {
                var prefix = this.name.replace('Style', '');
                var btnOpts = document.querySelector('.' + prefix + '-btn-options');
                if (btnOpts) {
                    btnOpts.style.display = (this.value === 'btn') ? '' : 'none';
                }
                updatePreview();
            });
        });

        // --- setting type toggle ---
        document.querySelectorAll('input[name="ndrGenType"]').forEach(function (radio) {
            radio.addEventListener('change', function () {
                var picker = document.getElementById('ndrSettingPicker');
                if (picker) picker.style.display = (this.value === 'setting') ? '' : 'none';
                updatePreview();
            });
        });

        // --- any .ndr-update field triggers preview ---
        document.querySelectorAll('.ndr-update').forEach(function (el) {
            el.addEventListener('change', updatePreview);
            el.addEventListener('input',  updatePreview);
        });

        // --- main tab change triggers preview ---
        document.querySelectorAll('#ndrTagTabs .nav-link').forEach(function (tab) {
            tab.addEventListener('shown.bs.tab', updatePreview);
        });

        // --- link sub-tab change triggers preview ---
        document.querySelectorAll('#ndrLinkTypeTabs .nav-link').forEach(function (tab) {
            tab.addEventListener('shown.bs.tab', updatePreview);
        });

        // --- Insert button ---
        var insertBtn = document.getElementById('ndrTagInsertBtn');
        if (insertBtn) {
            insertBtn.addEventListener('click', function () {
                var tagInfo = buildTag();
                if (!tagInfo || !_activeEditorId) return;

                insertIntoEditor(_activeEditorId, tagInfo);

                var modalEl = document.getElementById('ndrTagModal');
                if (modalEl) bootstrap.Modal.getOrCreateInstance(modalEl).hide();
            });
        }

    });

}());
