/**
 * NDR Core Grid Editor
 * Visual 12-column grid editor for configuring search form / result card fields.
 *
 * Interactions
 *   Place  : click a field in the palette to select it, then click any empty cell.
 *   Move   : drag the ⠿ handle on a placed field to a new empty cell.
 *   Resize : ← / → buttons (and ↑ / ↓ when allowRowSpan is true).
 *   Remove : × button — returns the field to the palette.
 *
 * Usage:
 *   new GridEditor({
 *     containerId:     'my-div',
 *     hiddenInputId:   'my-input',
 *     availableFields: [{id, label}, ...],
 *     allowRowSpan:    false,
 *     initialData:     [{field_id, label, row, col, col_span, row_span}, ...]
 *   });
 */
class GridEditor {

    constructor(options) {
        this.containerId     = options.containerId;
        this.hiddenInputId   = options.hiddenInputId;
        this.availableFields = options.availableFields || [];
        this.allowRowSpan    = options.allowRowSpan || false;
        this.placed          = [];
        this.numRows         = 2;

        // palette-click selection state
        this._selectedFieldId = null;

        // drag-move state (fieldId being dragged from a placed block)
        this._draggingFieldId = null;

        this.nextColorIdx = 0;
        this.fieldColors  = {};
        this.colorPalette = [
            '#0d6efd', '#6610f2', '#d63384', '#fd7e14',
            '#198754', '#20c997', '#0dcaf0', '#6c757d',
            '#0077b6', '#7b2d8b', '#e76f51', '#2a9d8f'
        ];

        this.container  = document.getElementById(this.containerId);
        this.hiddenInput = document.getElementById(this.hiddenInputId);

        if (!this.container || !this.hiddenInput) {
            console.error('GridEditor: #' + this.containerId + ' or #' + this.hiddenInputId + ' not found');
            return;
        }

        if (options.initialData && options.initialData.length > 0) {
            this._loadInitialData(options.initialData);
        }

        this._buildUI();
    }

    // -------------------------------------------------------------------------
    // Initialisation
    // -------------------------------------------------------------------------

    _loadInitialData(data) {
        this.placed = data.map(item => ({
            field_id : item.field_id,
            label    : item.label,
            row      : item.row,
            col      : item.col,
            col_span : item.col_span || 1,
            row_span : item.row_span || 1
        }));
        this.placed.forEach(item => {
            this.fieldColors[item.field_id] = this.colorPalette[this.nextColorIdx++ % this.colorPalette.length];
        });
        const maxRow = this.placed.reduce((m, p) => Math.max(m, p.row + p.row_span - 1), 0);
        this.numRows = Math.max(maxRow + 1, 2);
    }

    _buildUI() {
        this.container.innerHTML = '';

        // Outer layout: grid on left, palette on right
        const layout = document.createElement('div');
        layout.style.cssText = 'display:flex;gap:14px;align-items:flex-start;';

        // ---- grid area ----
        const gridArea = document.createElement('div');
        gridArea.style.cssText = 'flex:1;min-width:0;';

        // column-number header
        const header = document.createElement('div');
        header.style.cssText = 'display:grid;grid-template-columns:repeat(12,1fr);gap:3px;padding:0 3px;margin-bottom:2px;';
        for (let c = 1; c <= 12; c++) {
            const h = document.createElement('div');
            h.style.cssText = 'text-align:center;font-size:10px;color:#6c757d;font-weight:600;';
            h.textContent = c;
            header.appendChild(h);
        }

        // stable wrapper (never rebuilt)
        this._gridWrapper = document.createElement('div');
        this._gridWrapper.style.cssText = 'background:#dee2e6;border-radius:6px;padding:3px;position:relative;';

        const footer = document.createElement('div');
        footer.style.cssText = 'margin-top:6px;display:flex;gap:6px;';

        const addRowBtn = document.createElement('button');
        addRowBtn.type = 'button';
        addRowBtn.className = 'btn btn-sm btn-outline-secondary';
        addRowBtn.innerHTML = '<i class="fa-solid fa-plus"></i> Add Row';
        addRowBtn.addEventListener('click', () => { this.numRows++; this._redraw(); });

        const removeRowBtn = document.createElement('button');
        removeRowBtn.type = 'button';
        removeRowBtn.className = 'btn btn-sm btn-outline-secondary';
        removeRowBtn.innerHTML = '<i class="fa-solid fa-minus"></i> Remove Row';
        removeRowBtn.addEventListener('click', () => {
            if (this.numRows <= 1) return;
            const maxUsed = this.placed.reduce((m, p) => Math.max(m, p.row + p.row_span - 1), 0);
            if (this.numRows > maxUsed) { this.numRows--; this._redraw(); }
        });

        footer.appendChild(addRowBtn);
        footer.appendChild(removeRowBtn);

        gridArea.appendChild(header);
        gridArea.appendChild(this._gridWrapper);
        gridArea.appendChild(footer);

        // ---- palette ----
        this._paletteEl = document.createElement('div');
        this._paletteEl.style.cssText = 'width:175px;flex-shrink:0;background:#f8f9fa;border:1px solid #dee2e6;border-radius:6px;padding:10px;';

        const palTitle = document.createElement('div');
        palTitle.style.cssText = 'font-size:12px;font-weight:700;color:#495057;margin-bottom:4px;';
        palTitle.textContent = 'Available Fields';

        const palHint = document.createElement('div');
        palHint.style.cssText = 'font-size:10px;color:#6c757d;margin-bottom:8px;line-height:1.4;';
        palHint.textContent = 'Click a field to select it, then click an empty cell to place it.';

        this._paletteListEl = document.createElement('div');

        this._paletteEl.appendChild(palTitle);
        this._paletteEl.appendChild(palHint);
        this._paletteEl.appendChild(this._paletteListEl);

        layout.appendChild(gridArea);
        layout.appendChild(this._paletteEl);
        this.container.appendChild(layout);

        this._redraw();
    }

    // -------------------------------------------------------------------------
    // Redraw
    // -------------------------------------------------------------------------

    _redraw() {
        this._renderGrid();
        this._renderPalette();
        this._serialize();
    }

    _renderGrid() {
        this._gridWrapper.innerHTML = '';

        this._gridInner = document.createElement('div');
        this._gridInner.style.cssText =
            'display:grid;' +
            'grid-template-columns:repeat(12,1fr);' +
            'grid-template-rows:repeat(' + this.numRows + ',48px);' +
            'gap:3px;' +
            'position:relative;';

        const occ = this._buildOccupancyMap();

        for (let r = 1; r <= this.numRows; r++) {
            for (let c = 1; c <= 12; c++) {
                const cell = document.createElement('div');
                cell.dataset.row = r;
                cell.dataset.col = c;

                const isEmpty = !(occ[r] && occ[r][c]);

                cell.style.cssText =
                    'grid-column:' + c + ';' +
                    'grid-row:' + r + ';' +
                    'background:white;' +
                    'border-radius:3px;' +
                    'cursor:' + (isEmpty ? 'cell' : 'default') + ';' +
                    'transition:background 0.1s;';

                if (isEmpty) {
                    // Click-to-place: only on empty cells
                    cell.addEventListener('click', () => {
                        if (this._selectedFieldId !== null) {
                            this._placeField(this._selectedFieldId, r, c);
                        }
                    });
                }

                // Drag-move drop target: ALL cells (including occupied ones).
                // During a drag the moved block gets pointer-events:none, so these
                // background cells become reachable even under the dragged field.
                // _moveField() rejects overlaps, so dropping on another field is safe.
                {
                    cell.addEventListener('dragover', (e) => {
                        if (this._draggingFieldId === null) return;
                        e.preventDefault();
                        e.dataTransfer.dropEffect = 'move';
                        cell.style.background = '#cfe2ff';
                    });
                    cell.addEventListener('dragleave', () => {
                        cell.style.background = 'white';
                    });
                    cell.addEventListener('drop', (e) => {
                        e.preventDefault();
                        cell.style.background = 'white';
                        if (this._draggingFieldId !== null) {
                            this._moveField(this._draggingFieldId, r, c);
                        }
                    });
                }

                this._gridInner.appendChild(cell);
            }
        }

        // Placed field blocks (rendered on top of background cells via z-index)
        for (const item of this.placed) {
            this._gridInner.appendChild(this._buildFieldBlock(item));
        }

        this._gridWrapper.appendChild(this._gridInner);
    }

    // -------------------------------------------------------------------------
    // Field block
    // -------------------------------------------------------------------------

    _buildFieldBlock(item) {
        const color = this.fieldColors[item.field_id] || '#0d6efd';

        const block = document.createElement('div');
        block.className = 'ge-placed-field';
        block.dataset.fieldId = item.field_id;
        block.style.cssText =
            'grid-column:' + item.col + ' / ' + (item.col + item.col_span) + ';' +
            'grid-row:'    + item.row + ' / ' + (item.row + item.row_span) + ';' +
            'background:'  + color + ';' +
            'color:white;border-radius:4px;padding:4px 6px;' +
            'display:flex;align-items:center;justify-content:space-between;' +
            'z-index:10;position:relative;overflow:hidden;font-size:12px;user-select:none;';

        // Label
        const label = document.createElement('span');
        label.style.cssText = 'flex:1;overflow:hidden;text-overflow:ellipsis;white-space:nowrap;margin:0 4px;';
        label.textContent = item.label;

        // Controls
        const controls = document.createElement('div');
        controls.style.cssText = 'display:flex;gap:2px;flex-shrink:0;';

        const btnCss = 'background:rgba(255,255,255,0.25);border:none;color:white;padding:1px 5px;cursor:pointer;font-size:11px;border-radius:2px;line-height:1.5;';

        const mk = (text, title, handler) => {
            const b = document.createElement('button');
            b.type = 'button'; b.title = title;
            b.style.cssText = btnCss;
            b.textContent = text;
            b.addEventListener('click', (e) => { e.stopPropagation(); handler(); });
            return b;
        };

        // Drag-move handle — uses HTML5 draggable on the whole block
        const dragHandle = document.createElement('button');
        dragHandle.type = 'button';
        dragHandle.title = 'Drag to move';
        dragHandle.style.cssText = btnCss + 'cursor:grab;font-size:13px;padding:1px 4px;margin-right:2px;';
        dragHandle.textContent = '⠿';
        dragHandle.addEventListener('mousedown', (e) => e.stopPropagation());
        // Make the BLOCK draggable when the handle is pressed
        dragHandle.addEventListener('mousedown', () => { block.draggable = true; });
        dragHandle.addEventListener('mouseup',   () => { block.draggable = false; });

        if (this.allowRowSpan) {
            controls.appendChild(mk('↑', 'Decrease height', () => this._adjustHeight(item.field_id, -1)));
            controls.appendChild(mk('↓', 'Increase height', () => this._adjustHeight(item.field_id, +1)));
        }
        controls.appendChild(mk('←', 'Decrease width', () => this._adjustWidth(item.field_id, -1)));
        controls.appendChild(mk('→', 'Increase width',  () => this._adjustWidth(item.field_id, +1)));

        const removeBtn = mk('×', 'Remove field', () => this._removeField(item.field_id));
        removeBtn.style.cssText += 'margin-left:4px;font-size:13px;padding:0 4px;';
        controls.appendChild(removeBtn);

        block.appendChild(dragHandle);
        block.appendChild(label);
        block.appendChild(controls);

        // HTML5 drag events (block.draggable toggled by handle mousedown/up)
        block.addEventListener('dragstart', (e) => {
            this._draggingFieldId = item.field_id;
            e.dataTransfer.effectAllowed = 'move';
            // Defer so the browser captures the ghost image before we hide the block.
            // pointer-events:none lets the background cells underneath receive dragover/drop.
            setTimeout(() => {
                block.style.opacity = '0.4';
                block.style.pointerEvents = 'none';
            }, 0);
        });
        block.addEventListener('dragend', () => {
            block.draggable = false;
            block.style.opacity = '1';
            block.style.pointerEvents = '';
            this._draggingFieldId = null;
        });

        return block;
    }

    // -------------------------------------------------------------------------
    // Placement / movement
    // -------------------------------------------------------------------------

    _placeField(fieldId, row, col) {
        const field = this.availableFields.find(f => f.id === fieldId);
        if (!field) return;

        if (!this.fieldColors[fieldId]) {
            this.fieldColors[fieldId] = this.colorPalette[this.nextColorIdx++ % this.colorPalette.length];
        }

        this.placed.push({
            field_id: fieldId, label: field.label,
            row, col, col_span: 1, row_span: 1
        });

        this._selectedFieldId = null;
        this._redraw();
    }

    _moveField(fieldId, newRow, newCol) {
        const item = this.placed.find(p => p.field_id === fieldId);
        if (!item) return;

        // Check that all cells the moved field would occupy are free (except from itself)
        const testPlaced = this.placed.map(p =>
            p.field_id === fieldId
                ? { ...p, row: newRow, col: newCol }
                : p
        );
        if (this._hasOverlaps(testPlaced)) return;
        if (newCol + item.col_span - 1 > 12) return;
        if (newRow + item.row_span - 1 > this.numRows) this.numRows = newRow + item.row_span;

        item.row = newRow;
        item.col = newCol;
        this._redraw();
    }

    _removeField(fieldId) {
        this.placed = this.placed.filter(p => p.field_id !== fieldId);
        if (this._selectedFieldId === fieldId) this._selectedFieldId = null;
        this._redraw();
    }

    _adjustWidth(fieldId, delta) {
        const item = this.placed.find(p => p.field_id === fieldId);
        if (!item) return;
        const newSpan = item.col_span + delta;
        if (newSpan < 1 || item.col + newSpan - 1 > 12) return;
        const test = this.placed.map(p => p.field_id === fieldId ? { ...p, col_span: newSpan } : p);
        if (this._hasOverlaps(test)) return;
        item.col_span = newSpan;
        this._redraw();
    }

    _adjustHeight(fieldId, delta) {
        const item = this.placed.find(p => p.field_id === fieldId);
        if (!item) return;
        const newSpan = item.row_span + delta;
        if (newSpan < 1) return;
        const test = this.placed.map(p => p.field_id === fieldId ? { ...p, row_span: newSpan } : p);
        if (this._hasOverlaps(test)) return;
        if (item.row + newSpan - 1 >= this.numRows) this.numRows = item.row + newSpan;
        item.row_span = newSpan;
        this._redraw();
    }

    // -------------------------------------------------------------------------
    // Palette
    // -------------------------------------------------------------------------

    _renderPalette() {
        this._paletteListEl.innerHTML = '';
        const available = this._getAvailableFields();

        if (available.length === 0) {
            const msg = document.createElement('div');
            msg.style.cssText = 'font-size:11px;color:#6c757d;font-style:italic;';
            msg.textContent = 'All fields placed.';
            this._paletteListEl.appendChild(msg);
            return;
        }

        available.forEach(f => {
            const isSelected = this._selectedFieldId === f.id;
            const item = document.createElement('div');
            item.style.cssText =
                'padding:6px 9px;margin-bottom:4px;border-radius:4px;font-size:12px;cursor:pointer;' +
                'border:2px solid ' + (isSelected ? '#0d6efd' : 'transparent') + ';' +
                'background:' + (isSelected ? '#cfe2ff' : '#e9ecef') + ';' +
                'color:' + (isSelected ? '#0a4492' : '#212529') + ';' +
                'font-weight:' + (isSelected ? '600' : 'normal') + ';' +
                'transition:background 0.1s;';
            item.textContent = f.label;
            item.title = isSelected ? 'Click an empty cell to place this field' : 'Click to select';

            item.addEventListener('click', () => {
                this._selectedFieldId = (this._selectedFieldId === f.id) ? null : f.id;
                this._renderPalette(); // re-render palette to update highlight
            });

            this._paletteListEl.appendChild(item);
        });

        // Show selected-field hint below list
        if (this._selectedFieldId !== null) {
            const hint = document.createElement('div');
            hint.style.cssText = 'margin-top:8px;font-size:10px;color:#0d6efd;line-height:1.4;';
            hint.innerHTML = '<i class="fa-solid fa-circle-info"></i> Click an empty cell on the grid to place the selected field.';
            this._paletteListEl.appendChild(hint);
        }
    }

    // -------------------------------------------------------------------------
    // Utilities
    // -------------------------------------------------------------------------

    _buildOccupancyMap() {
        const map = {};
        for (const item of this.placed) {
            for (let r = item.row; r < item.row + item.row_span; r++) {
                if (!map[r]) map[r] = {};
                for (let c = item.col; c < item.col + item.col_span; c++) {
                    map[r][c] = item.field_id;
                }
            }
        }
        return map;
    }

    _hasOverlaps(placed) {
        const map = {};
        for (const item of placed) {
            for (let r = item.row; r < item.row + item.row_span; r++) {
                if (!map[r]) map[r] = {};
                for (let c = item.col; c < item.col + item.col_span; c++) {
                    if (map[r][c] !== undefined) return true;
                    map[r][c] = item.field_id;
                }
            }
        }
        return false;
    }

    _getAvailableFields() {
        const placed = new Set(this.placed.map(p => p.field_id));
        return this.availableFields.filter(f => !placed.has(f.id));
    }

    _serialize() {
        this.hiddenInput.value = JSON.stringify(
            this.placed.map(item => ({
                field_id: item.field_id,
                row:      item.row,
                col:      item.col,
                col_span: item.col_span,
                row_span: item.row_span
            }))
        );
    }
}