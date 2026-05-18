/**
 * NDR Result Field Tag Inserter
 *
 * Injects an "Insert Field Tag" button above every CKEditor5 field that carries
 * the data-ndr-result-editor attribute. Clicking it opens a Bootstrap modal;
 * on confirm the generated {variable|filter:param=val} tag is inserted at cursor.
 * Supports up to three chained filters per tag.
 */
(function () {
    'use strict';

    var _activeEditorId = null;

    // ------------------------------------------------------------------ //
    // Filter slot descriptors                                              //
    // ------------------------------------------------------------------ //

    var VAR_SLOTS = [
        { selectId: 'ndrRtVarFilter1', paramAreaId: 'ndrRtVarParamArea1', hintId: 'ndrRtVarFilterHint1', wrapId: null },
        { selectId: 'ndrRtVarFilter2', paramAreaId: 'ndrRtVarParamArea2', hintId: 'ndrRtVarFilterHint2', wrapId: 'ndrRtVarFilter2Wrap' },
        { selectId: 'ndrRtVarFilter3', paramAreaId: 'ndrRtVarParamArea3', hintId: 'ndrRtVarFilterHint3', wrapId: 'ndrRtVarFilter3Wrap' }
    ];

    var LIT_SLOTS = [
        { selectId: 'ndrRtLitFilter1', paramAreaId: 'ndrRtLitParamArea1', hintId: 'ndrRtLitFilterHint1', wrapId: null },
        { selectId: 'ndrRtLitFilter2', paramAreaId: 'ndrRtLitParamArea2', hintId: 'ndrRtLitFilterHint2', wrapId: 'ndrRtLitFilter2Wrap' },
        { selectId: 'ndrRtLitFilter3', paramAreaId: 'ndrRtLitParamArea3', hintId: 'ndrRtLitFilterHint3', wrapId: 'ndrRtLitFilter3Wrap' }
    ];

    // ------------------------------------------------------------------ //
    // Filter metadata (mirrors ndr_core/ndr_templatetags/filters.py)      //
    // ------------------------------------------------------------------ //

    // Filter groups define the <optgroup> order and labels.
    var FILTER_GROUPS = [
        { key: 'text',        label: 'Text' },
        { key: 'number_date', label: 'Numbers & Dates' },
        { key: 'display',     label: 'Display' },
        { key: 'links_media', label: 'Links & Media' },
        { key: 'collections', label: 'Collections' },
        { key: 'advanced',    label: 'Advanced' }
    ];

    var FILTERS = [
        // ── Text ──────────────────────────────────────────────────────────
        { group: 'text', name: 'default',    label: 'Default value', hint: 'Render a fallback when the field is empty.',           params: [{ id: 'p_default_value', key: 'value', label: 'Fallback', placeholder: 'N/A' }] },
        { group: 'text', name: 'upper',      label: 'Uppercase',     hint: 'Convert text to UPPER CASE.',                          params: [] },
        { group: 'text', name: 'lower',      label: 'Lowercase',     hint: 'Convert text to lower case.',                          params: [] },
        { group: 'text', name: 'title',      label: 'Title case',    hint: 'Convert text to Title Case.',                          params: [] },
        { group: 'text', name: 'capitalize', label: 'Capitalize',    hint: 'Capitalize the first letter.',                         params: [] },
        { group: 'text', name: 'truncate',   label: 'Truncate',      hint: 'Limit the text to a maximum number of characters.',    params: [{ id: 'p_truncate_length', key: 'length', label: 'Max chars', placeholder: '200' }] },

        // ── Numbers & Dates ───────────────────────────────────────────────
        { group: 'number_date', name: 'date',     label: 'Date',            hint: 'Format a date value.',                                    params: [{ id: 'p_date_format', key: 'format', label: 'Format string', placeholder: '%Y-%m-%d' }] },
        { group: 'number_date', name: 'relative', label: 'Relative date',   hint: 'Show date relative to today ("2 days ago").',             params: [] },
        { group: 'number_date', name: 'format',   label: 'Number format',   hint: 'Format a number with a Python format string.',            params: [{ id: 'p_number_format', key: 'format', label: 'Format string', placeholder: '.2f' }] },
        { group: 'number_date', name: 'readable', label: 'Readable number', hint: 'Format a large number in a human-readable way (1 234 567).', params: [] },
        { group: 'number_date', name: 'compact',  label: 'Compact number',  hint: 'Compact number format (e.g. 1.2M).',                      params: [] },

        // ── Display ───────────────────────────────────────────────────────
        { group: 'display', name: 'badge', label: 'Badge', hint: 'Wrap value in a Bootstrap badge. Color accepts Bootstrap names, CSS values, "byval", or "gradient".', params: [
            { id: 'p_badge_color', key: 'color', label: 'Text color',        widget: 'color', placeholder: 'white' },
            { id: 'p_badge_bg',    key: 'bg',    label: 'Background color',  widget: 'color', placeholder: 'primary' },
            { id: 'p_badge_field', key: 'field', label: 'Fieldify (lookup field name)', widget: 'text', placeholder: '' },
            { id: 'p_badge_tt',    key: 'tt',    label: 'Tooltip text',      widget: 'text', placeholder: '' }
        ]},
        { group: 'display', name: 'pill', label: 'Pill badge', hint: 'Wrap value in a Bootstrap rounded pill badge.', params: [
            { id: 'p_pill_color', key: 'color', label: 'Text color',        widget: 'color', placeholder: 'white' },
            { id: 'p_pill_bg',    key: 'bg',    label: 'Background color',  widget: 'color', placeholder: 'secondary' },
            { id: 'p_pill_field', key: 'field', label: 'Fieldify (lookup field name)', widget: 'text', placeholder: '' },
            { id: 'p_pill_tt',    key: 'tt',    label: 'Tooltip text',      widget: 'text', placeholder: '' }
        ]},
        { group: 'display', name: 'bool',  label: 'Boolean',    hint: 'Convert a boolean to custom true/false strings.', params: [{ id: 'p_bool_true', key: 'true', label: 'True label', placeholder: 'Yes' }, { id: 'p_bool_false', key: 'false', label: 'False label', placeholder: 'No' }] },
        { group: 'display', name: 'code',  label: 'Code block', hint: 'Render the value inside a syntax-highlighted code block.', params: [{ id: 'p_code_lang', key: 'lang', label: 'Language', placeholder: 'json' }] },

        // ── Links & Media ─────────────────────────────────────────────────
        { group: 'links_media', name: 'linkify',  label: 'Linkify',   hint: 'Turn a URL value into a clickable link.',      params: [{ id: 'p_linkify_label', key: 'label', label: 'Link text', placeholder: '' }] },
        { group: 'links_media', name: 'weblinks', label: 'Web links', hint: 'Render a list of URLs as links.',               params: [] },
        { group: 'links_media', name: 'img',      label: 'Image',     hint: 'Render a URL value as an <img> element.',       params: [{ id: 'p_img_width', key: 'width', label: 'Width', placeholder: '100%' }, { id: 'p_img_height', key: 'height', label: 'Height', placeholder: '' }] },
        { group: 'links_media', name: 'iframe',   label: 'IFrame',    hint: 'Embed a URL inside an iframe.',                 params: [{ id: 'p_iframe_width', key: 'width', label: 'Width', placeholder: '100%' }, { id: 'p_iframe_height', key: 'height', label: 'Height', placeholder: '400px' }] },

        // ── Collections ───────────────────────────────────────────────────
        { group: 'collections', name: 'list',      label: 'List',      hint: 'Render an array as an HTML list.',                          params: [{ id: 'p_list_type', key: 'type', label: 'Type (ul / ol)', placeholder: 'ul' }, { id: 'p_list_limit', key: 'limit', label: 'Limit items', placeholder: '' }] },
        { group: 'collections', name: 'table',     label: 'Table',     hint: 'Render a list of objects as an HTML table.',               params: [{ id: 'p_table_class', key: 'class', label: 'CSS class', placeholder: 'table table-sm' }] },
        { group: 'collections', name: 'datatable', label: 'DataTable', hint: 'Render a list of objects as an interactive DataTable.',    params: [{ id: 'p_datatable_class', key: 'class', label: 'CSS class', placeholder: 'table' }] },

        // ── Advanced ──────────────────────────────────────────────────────
        { group: 'advanced', name: 'fieldify', label: 'Fieldify',     hint: 'Look up a human-readable label for a coded value via a search field definition.', params: [{ id: 'p_fieldify_field', key: 'field', label: 'Field name', placeholder: 'my_field' }] },
        { group: 'advanced', name: 'map',      label: 'Map',          hint: 'Render a geo-coordinate as a map.',                         params: [{ id: 'p_map_lat', key: 'lat', label: 'Latitude field', placeholder: 'geo.lat' }, { id: 'p_map_lon', key: 'lon', label: 'Longitude field', placeholder: 'geo.lon' }] },
        { group: 'advanced', name: 'plotly',   label: 'Plotly chart', hint: 'Render a Plotly.js chart from a JSON value.',               params: [] }
    ];

    // ------------------------------------------------------------------ //
    // Button injection                                                     //
    // ------------------------------------------------------------------ //

    function injectButton(editorId) {
        var editorEl = document.getElementById(editorId);
        if (!editorEl) return;
        var parent = editorEl.parentElement;
        if (!parent) return;
        if (parent.querySelector('.ndr-result-tag-btn[data-editor-id="' + editorId + '"]')) return;
        var ckEditor = parent.querySelector('.ck-editor');
        if (!ckEditor) return;

        var btn = document.createElement('button');
        btn.type = 'button';
        btn.className = 'btn btn-sm btn-outline-secondary mb-1 ndr-result-tag-btn';
        btn.dataset.editorId = editorId;
        btn.innerHTML = '<i class="fa-solid fa-brackets-curly"></i> Insert Field Tag';
        btn.addEventListener('click', function () { openModal(editorId); });
        parent.insertBefore(btn, ckEditor);
    }

    function setupEditor(editorId) {
        if (window.editors && window.editors[editorId]) {
            injectButton(editorId);
        } else if (window.ckeditorRegisterCallback) {
            window.ckeditorRegisterCallback(editorId, function () { injectButton(editorId); });
        }
    }

    // ------------------------------------------------------------------ //
    // Modal open / reset                                                   //
    // ------------------------------------------------------------------ //

    function openModal(editorId) {
        _activeEditorId = editorId;
        resetModal();
        updatePreview();
        var modalEl = document.getElementById('ndrResultTagModal');
        if (!modalEl) return;
        bootstrap.Modal.getOrCreateInstance(modalEl).show();
    }

    function resetModal() {
        var varPath = document.getElementById('ndrRtVarPath');
        if (varPath) varPath.value = '';
        var literal = document.getElementById('ndrRtLiteralText');
        if (literal) literal.value = '';

        resetSlots(VAR_SLOTS);
        resetSlots(LIT_SLOTS);

        // Reset to Variable tab
        var firstTab = document.getElementById('ndrRt-tab-variable');
        if (firstTab) bootstrap.Tab.getOrCreateInstance(firstTab).show();
    }

    // ------------------------------------------------------------------ //
    // Slot helpers                                                         //
    // ------------------------------------------------------------------ //

    function resetSlots(slots) {
        slots.forEach(function (slot) {
            var sel = document.getElementById(slot.selectId);
            if (sel) sel.value = '';
            var area = document.getElementById(slot.paramAreaId);
            if (area) area.innerHTML = '';
            var hint = document.getElementById(slot.hintId);
            if (hint) hint.textContent = '';
            if (slot.wrapId) {
                var wrap = document.getElementById(slot.wrapId);
                if (wrap) wrap.classList.add('d-none');
            }
        });
    }

    function onFilterChange(slots, slotIndex) {
        var slot = slots[slotIndex];
        var sel = document.getElementById(slot.selectId);
        var filterName = sel ? sel.value : '';

        renderFilterParams(filterName, slot.paramAreaId);
        updateFilterHint(filterName, slot.hintId);

        // Show or hide the next slot
        if (slotIndex + 1 < slots.length) {
            var nextSlot = slots[slotIndex + 1];
            var nextWrap = document.getElementById(nextSlot.wrapId);
            if (nextWrap) {
                if (filterName) {
                    nextWrap.classList.remove('d-none');
                } else {
                    // Hide and reset all subsequent slots
                    resetSlots(slots.slice(slotIndex + 1));
                }
            }
        }

        updatePreview();
    }

    function populateFilterSelect(sel) {
        FILTER_GROUPS.forEach(function (group) {
            var groupFilters = FILTERS.filter(function (f) { return f.group === group.key; });
            if (!groupFilters.length) return;
            var optgroup = document.createElement('optgroup');
            optgroup.label = group.label;
            groupFilters.forEach(function (f) {
                var opt = document.createElement('option');
                opt.value = f.name;
                opt.textContent = f.label + ' (' + f.name + ')';
                optgroup.appendChild(opt);
            });
            sel.appendChild(optgroup);
        });
    }

    // ------------------------------------------------------------------ //
    // Color widget                                                         //
    // ------------------------------------------------------------------ //

    var COLOR_SWATCHES = [
        { color: 'white',     style: 'background:#fff;color:#000;border:1px solid #ced4da' },
        { color: 'primary',   style: 'background:var(--bs-primary,#0d6efd);color:#fff' },
        { color: 'secondary', style: 'background:var(--bs-secondary,#6c757d);color:#fff' },
        { color: 'success',   style: 'background:var(--bs-success,#198754);color:#fff' },
        { color: 'danger',    style: 'background:var(--bs-danger,#dc3545);color:#fff' },
        { color: 'warning',   style: 'background:var(--bs-warning,#ffc107);color:#000' },
        { color: 'info',      style: 'background:var(--bs-info,#0dcaf0);color:#000' },
        { color: 'light',     style: 'background:var(--bs-light,#f8f9fa);color:#000;border:1px solid #ced4da' },
        { color: 'dark',      style: 'background:var(--bs-dark,#212529);color:#fff' }
    ];

    var COLOR_SPECIALS = [
        { color: 'byval',    title: 'Auto-derive a color from the field value (consistent per value)' },
        { color: 'gradient', title: 'Red → green gradient based on numeric value (0–100)' }
    ];

    function buildColorWidget(uid, p) {
        var html = '<label for="' + uid + '_txt" class="form-label form-label-sm">' + p.label + '</label>';
        html += '<div class="d-flex flex-wrap gap-1 mb-1 align-items-center">';

        COLOR_SWATCHES.forEach(function (s) {
            html += '<button type="button" class="ndrRt-color-swatch btn btn-sm"'
                  + ' style="' + s.style + ';width:30px;height:22px;padding:0;font-size:9px;"'
                  + ' data-color="' + s.color + '" data-target="' + uid + '_txt"'
                  + ' title="' + s.color + '"></button>';
        });

        COLOR_SPECIALS.forEach(function (s) {
            html += '<button type="button" class="ndrRt-color-swatch btn btn-sm btn-outline-secondary"'
                  + ' style="height:22px;padding:0 5px;font-size:10px;"'
                  + ' data-color="' + s.color + '" data-target="' + uid + '_txt"'
                  + ' title="' + s.title + '">' + s.color + '</button>';
        });

        html += '</div>';
        html += '<input type="text" class="form-control form-control-sm"'
              + ' id="' + uid + '_txt" placeholder="' + (p.placeholder || '') + '"'
              + ' data-param-key="' + p.key + '">';
        return html;
    }

    function buildTextWidget(uid, p) {
        return '<label for="' + uid + '" class="form-label form-label-sm">' + p.label + '</label>'
             + '<input type="text" class="form-control form-control-sm"'
             + ' id="' + uid + '" placeholder="' + (p.placeholder || '') + '"'
             + ' data-param-key="' + p.key + '">';
    }

    // ------------------------------------------------------------------ //
    // Filter param rendering                                               //
    // ------------------------------------------------------------------ //

    function renderFilterParams(filterName, paramAreaId) {
        var area = document.getElementById(paramAreaId);
        if (!area) return;
        area.innerHTML = '';
        if (!filterName) return;

        var filter = FILTERS.find(function (f) { return f.name === filterName; });
        if (!filter || filter.params.length === 0) return;

        filter.params.forEach(function (p) {
            var uid = paramAreaId + '_' + p.id;
            var wrap = document.createElement('div');
            wrap.className = 'mb-2';
            wrap.innerHTML = (p.widget === 'color') ? buildColorWidget(uid, p) : buildTextWidget(uid, p);
            area.appendChild(wrap);
        });

        // Wire text inputs → preview
        area.querySelectorAll('input[data-param-key]').forEach(function (el) {
            el.addEventListener('input', updatePreview);
        });

        // Wire color swatches → fill input + preview
        area.querySelectorAll('.ndrRt-color-swatch').forEach(function (btn) {
            btn.addEventListener('click', function () {
                var input = document.getElementById(this.dataset.target);
                if (input) {
                    input.value = this.dataset.color;
                    updatePreview();
                }
            });
        });
    }

    function updateFilterHint(filterName, hintId) {
        var hint = document.getElementById(hintId);
        if (!hint) return;
        var filter = FILTERS.find(function (f) { return f.name === filterName; });
        hint.textContent = filter ? filter.hint : '';
    }

    // ------------------------------------------------------------------ //
    // Tag builder                                                          //
    // ------------------------------------------------------------------ //

    function buildFilterChain(slots) {
        var result = '';
        slots.forEach(function (slot) {
            var sel = document.getElementById(slot.selectId);
            if (!sel || !sel.value) return;
            var filterName = sel.value;
            var area = document.getElementById(slot.paramAreaId);
            var paramParts = [];
            if (area) {
                area.querySelectorAll('[data-param-key]').forEach(function (inp) {
                    var val = inp.value.trim();
                    if (val) paramParts.push(inp.dataset.paramKey + '=' + val);
                });
            }
            result += '|' + filterName + (paramParts.length ? ':' + paramParts.join(',') : '');
        });
        return result;
    }

    function buildTag() {
        var activeTab = document.querySelector('#ndrRtTabs .nav-link.active');
        if (!activeTab) return null;
        var target = activeTab.dataset.bsTarget;
        if (target === '#ndrRtTabVariable') return buildVariableTag();
        if (target === '#ndrRtTabLiteral')  return buildLiteralTag();
        return null;
    }

    function buildVariableTag() {
        var path = (document.getElementById('ndrRtVarPath').value || '').trim();
        if (!path) return null;
        return { tag: '{' + path + buildFilterChain(VAR_SLOTS) + '}' };
    }

    function buildLiteralTag() {
        var text = (document.getElementById('ndrRtLiteralText').value || '').trim();
        if (!text) return null;
        var chain = buildFilterChain(LIT_SLOTS);
        return { tag: '{"' + text + '"' + chain + '}' };
    }

    // ------------------------------------------------------------------ //
    // Live preview                                                         //
    // ------------------------------------------------------------------ //

    function updatePreview() {
        var preview = document.getElementById('ndrRtTagPreview');
        if (!preview) return;
        var tagInfo = buildTag();
        preview.textContent = tagInfo ? tagInfo.tag : '';
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
            if (!selection.isCollapsed) {
                writer.remove(selection.getFirstRange());
            }
            writer.insertText(tagInfo.tag, selection.getFirstPosition());
        });
    }

    // ------------------------------------------------------------------ //
    // Event wiring                                                         //
    // ------------------------------------------------------------------ //

    document.addEventListener('DOMContentLoaded', function () {

        // Detect and set up all result-editor fields
        document.querySelectorAll('[data-ndr-result-editor]').forEach(function (el) {
            setupEditor(el.id);
        });

        // Populate filter selects and wire change events for both slot groups
        [VAR_SLOTS, LIT_SLOTS].forEach(function (slots) {
            slots.forEach(function (slot, i) {
                var sel = document.getElementById(slot.selectId);
                if (!sel) return;
                populateFilterSelect(sel);
                sel.addEventListener('change', function () { onFilterChange(slots, i); });
            });
        });

        // Wire path / literal text inputs to preview
        document.querySelectorAll('.ndrRt-update').forEach(function (el) {
            el.addEventListener('input',  updatePreview);
            el.addEventListener('change', updatePreview);
        });

        // Tab change → preview
        document.querySelectorAll('#ndrRtTabs .nav-link').forEach(function (tab) {
            tab.addEventListener('shown.bs.tab', updatePreview);
        });

        // Field path hint chips
        document.querySelectorAll('.ndrRt-field-chip').forEach(function (chip) {
            chip.addEventListener('click', function () {
                var pathInput = document.getElementById('ndrRtVarPath');
                if (pathInput) {
                    pathInput.value = this.dataset.path;
                    updatePreview();
                }
            });
        });

        // Insert button
        var insertBtn = document.getElementById('ndrRtInsertBtn');
        if (insertBtn) {
            insertBtn.addEventListener('click', function () {
                var tagInfo = buildTag();
                if (!tagInfo || !_activeEditorId) return;
                insertIntoEditor(_activeEditorId, tagInfo);
                var modalEl = document.getElementById('ndrResultTagModal');
                if (modalEl) bootstrap.Modal.getOrCreateInstance(modalEl).hide();
            });
        }

    });

}());