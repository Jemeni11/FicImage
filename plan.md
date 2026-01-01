# FicImage v5 Image Compression Refactor - Complete Agenda (Final)

## 1. Core Compression Functions

### 1.1 New Smart Compression

- `compress_image_smart()` - Binary search for optimal quality with caching
- Returns `tuple[int, bytes]` (quality, compressed_data)
- Strips metadata except orientation EXIF
- Quality range: 50-95
- **If compression fails + `allow_resizing: false`** → return oversized image with warning
- **If compression fails + `allow_resizing: true`** → fallback to `resize_image_legacy()`

### 1.2 Legacy Resize Function

- Rename `compress_image()` → `resize_image_legacy()`
- Keep existing pixel calculation logic
- Only called when `allow_resizing: true` AND compression fails

## 2. Format Selection Logic

### 2.1 Helper Functions

- `has_transparency(image: Image.Image) -> bool` - Check alpha channel
- `has_animation(image: Image.Image) -> bool` - Check for multiple frames
- `select_image_format(image, target_output, user_preference) -> str` - Smart format picker

### 2.2 Format Capability Matrix

```python
FORMAT_CAPABILITIES = {
    "epub": {"transparency": "webp", "animation": "webp"},
    "html": {"transparency": "webp", "animation": "webp"},
    "pdf": {"transparency": "png", "animation": "webp"},
    "mobi": {"transparency": "png", "animation": None},  # No animation support
}
NO_TRANSPARENCY_FORMATS = "jpeg"

# we don't need arrays, just the best format for each case
# webp is best for transparency and animation where supported
# png is best for transparency where webp not supported
# jpeg is fallback for no transparency
```

### 2.3 Override Rules (Dict-Based)

- `resolve_format_override(image, target_output, user_format)` using capability matrix
- **Transparent image + user selected JPEG:**
  - PDF → PNG (JPEG doesn't support transparency)
  - MOBI → PNG (Kindle doesn't support transparency or WebP)
  - EPUB/HTML → WebP (optimal format, supports transparency)
- **Animated image:**
  - MOBI → Flatten to JPEG first frame (MOBI doesn't support animation)
  - EPUB/HTML/PDF → WebP (supports animation)
- **User choice respected when compatible** (no override needed)

## 3. Config File Structure

### 3.1 New Config Schema

```json
{
  "compress_images": true,
  "allow_resizing": false,
  "max_image_size": 100000,
  "formats": {
    "epub": "webp",
    "mobi": "jpeg",
    "html": "webp",
    "pdf": "webp"
  },
  "zip_embed_images": false
}
```

### 3.2 Config Validation

- `validate_formats()` - Check formats dict structure
- Handle missing keys (use defaults)
- Validate format values per output type
- Backwards compatibility for old config files

### 3.3 Migration Logic

- Old config without `formats` key → use smart defaults
- Old `default_image_format` → map to `formats["epub"]` only (v4 only supported EPUB)
- New formats (MOBI/HTML/PDF) get optimal defaults: `jpeg`, `webp`, `webp`
- Print one-time migration notice

## 4. Function Signature Updates

### 4.1 Thread Target Format Through Call Chain

```python
update_epub(file_path)
  └─> get_image_from_url(..., target_format="epub")
      └─> handle_image_data(..., target_format="epub")
          └─> select_image_format(image, "epub", user_pref)
```

### 4.2 Updated Signatures

- `get_image_from_url(url, target_format, compress, max_size)`
- `handle_image_data(content, target_format, compress, max_size)`
- `handle_base64_image(url, target_format, compress, max_size)`

## 5. Image Processing Pipeline

### 5.1 New Flow

```md
Download image
↓
Detect properties (transparency/animation)
↓
Check if already in target format
↓ (if yes, skip conversion but continue to metadata/compression)
Select format (based on output type + properties)
↓
Strip metadata (keep orientation EXIF)
↓
Convert format (if needed, e.g., PNG → WebP)
↓
Check size after conversion
↓
Compress if needed (binary search quality OR resize fallback)
↓
Return (bytes, format, mime_type)
```

### 5.2 Special Cases

- **Format conversion skipped if already in target format** (WebP → WebP optimization)
- **Metadata stripping always happens** (free optimization)
- **Quality compression only if needed** (skip if under max_size after conversion)
- SVG: Skip all processing, return as-is
- Already optimal: Skip compression if under max_size after format conversion
- Compression failure + `allow_resizing: false`: Return oversized with warning
- Compression failure + `allow_resizing: true`: Fall back to resize

## 6. Backwards Compatibility

### 6.1 Old Config Files

- Default to smart compression
- Map old `default_image_format` → `formats["epub"]` only (v4 only supported EPUB)
- New formats (MOBI/HTML/PDF) use optimal defaults
- Print migration message once

### 6.2 User Communication

```sh
[FicImage]: Using new smart compression (quality-based, preserves dimensions).
            Old resize-based compression available with "allow_resizing": true.
[Config Migration]: Detected old 'default_image_format' setting.
[Config Migration]: Using '<format>' for EPUB (your v4 setting).
[Config Migration]: New formats (MOBI/HTML/PDF) using smart defaults.
```

## 7. Testing & Edge Cases

### 7.1 Test Scenarios

- Tiny images (<10KB)
- Huge images (>5MB)
- Already-optimized WebPs
- Transparent PNGs
- Animated GIFs/WebPs
- Corrupted/invalid images
- SVGs
- Images already in target format (WebP → WebP)

### 7.2 Edge Case Handling

- User sets JPEG for transparent image → override based on capability matrix + warning
- User sets WebP for MOBI → override to JPEG + warning
- Compression fails to meet max_size + `allow_resizing: false` → return oversized + warning
- Compression fails to meet max_size + `allow_resizing: true` → resize fallback
- Animation on MOBI → flatten to first frame + info message
- Image already under max_size after format conversion → skip quality reduction
- Image already in target format → skip conversion, proceed to metadata stripping

## 8. Documentation Updates

### 8.1 README Changes

- Update compression section
- Document new `formats` config option
- Migration guide for v4 → v5 users
- Explain format conversion vs compression
- Document capability matrix behavior

### 8.2 Config File Comments

- Example with all new options
- Explain format selection logic
- Document `allow_resizing` behavior
- Show format capability matrix

## Implementation Order

1. **Phase 1**: Helper functions (#2.1) + Format capability matrix (#2.2)
2. **Phase 2**: Format selection logic with dict-based overrides (#2.3)
3. **Phase 3**: Config structure + validation (#3)
4. **Phase 4**: New compression function (#1.1)
5. **Phase 5**: Thread format through call chain (#4)
6. **Phase 6**: Integration + testing (#7)
7. **Phase 7**: Migration + docs (#6, #8)
