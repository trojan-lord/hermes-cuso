# Discord File Upload & MEDIA: Technical Reference

Condensed from Discord API docs and Hermes source code analysis (July 2026).

## Discord API: File Uploads

Source: https://discord.com/developers/reference#uploading-files

- **Per-file size limit**: 10 MiB default; higher with Nitro/Boost tier
- **Multipart form-data**: Files uploaded via `files[n]` parameter (must be uniquely named: `files[0]`, `files[1]`, etc.)
- **Max attachments per message**: 10 file attachments
- **Content-Type**: Must use `multipart/form-data` (not `application/json`)
- **Embeds**: Images can be referenced in embeds via `attachment://filename.png` URL scheme
- **Only image types for embed images**: `.jpg`, `.jpeg`, `.png`, `.webp`, `.gif`

### Message limits
- Text content: 2000 characters max (Hermes Discord adapter: `MAX_MESSAGE_LENGTH = 2000`)
- Messages are auto-chunked by `truncate_message()` at 2000 chars

## Hermes Discord Adapter: Media Delivery Flow

### Key methods (in `plugins/platforms/discord/adapter.py`):
- `send()` (line 1988) — text-only message, chunks at 2000 chars
- `_send_file_attachment()` (line 2428) — single file as attachment
- `send_multiple_images()` (line 2461) — batches up to 10 images in one message
- `send_voice()` (line 2607) — audio as native voice message (flags=8192) or fallback to file attachment

### Voice message delivery
`send_voice()` attempts:
1. Native voice message via raw API (`flags=8192`) with `.ogg` files — renders as Discord voice UI (play button, waveform, duration)
2. Falls back to regular file attachment if native voice fails
3. For forum channels (type 15): creates a thread post with audio as starter attachment

### MEDIA: tag regex (`MEDIA_TAG_CLEANUP_RE` in `gateway/platforms/base.py`)
Only strips tags whose path ends in a known deliverable extension. Unknown extensions are left for the bare-path detector downstream. Paths must start with `~/`, `/`, or Windows drive letter.

### Supported delivery extensions (in order of category):
- **Images**: `.png`, `.jpg`, `.jpeg`, `.gif`, `.webp`, `.bmp`, `.tiff`, `.svg`
- **Video**: `.mp4`, `.mov`, `.avi`, `.mkv`, `.webm`
- **Audio**: `.mp3`, `.wav`, `.ogg`, `.opus`, `.m4a`, `.flac`
- **Documents**: `.pdf`, `.docx`, `.doc`, `.odt`, `.rtf`, `.txt`, `.md`, `.epub`
- **Data**: `.xlsx`, `.xls`, `.ods`, `.csv`, `.tsv`, `.json`, `.xml`, `.yaml`, `.yml`
- **Presentations**: `.pptx`, `.ppt`, `.odp`, `.key`
- **Archives**: `.zip`, `.tar`, `.gz`, `.tgz`, `.bz2`, `.xz`, `.7z`, `.rar`

### Post-stream delivery (`_deliver_media_from_response` in `gateway/run.py`)
After streaming finishes, this function:
1. Calls `adapter.extract_media(response)` to find MEDIA: tags
2. Partitions files into images vs non-images
3. Images → `send_multiple_images()` (batches of 10)
4. Audio with `[[audio_as_voice]]` directive → `send_voice()`
5. Video → `send_video()`
6. Everything else → `send_document()` / `_send_file_attachment()`
