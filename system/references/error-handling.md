# Error Handling Reference

## Download Errors
| Error | Cause | Fix |
|-------|-------|-----|
| yt-dlp fails | Video unavailable | Tell user, ask for manual path |
| Region locked | Geo-restriction | Tell user, suggest VPN |
| Age restricted | YouTube age gate | Tell user, manual download |
| Network timeout | Connection issue | Retry once, then tell user |

## Subtitle Errors
| Error | Cause | Fix |
|-------|-------|-----|
| No SRT found | Video has no CC | Ask: "Use FunClip to transcribe?" |
| SRT timing wrong | Auto-generated errors | Manual review needed |
| Mixed languages | Multilingual CC | Filter to primary language |

## Video Processing Errors
| Error | Cause | Fix |
|-------|-------|-----|
| Source not 16:9 | Different aspect ratio | Use dynamic crop formula |
| Video < 5 min | Too short | Reduce to 3-5 clips |
| Video > 1 hour | Too long | Cap at 20 clips |
| Corrupt video | Bad download | Re-download or skip |
| Codec unsupported | Rare codec | Convert first with video_convert |

## FFmpeg Errors (the only encoder — kinocut removed from this project)
| Error | Cause | Fix |
|-------|-------|-----|
| Exit code 1, but output file exists | ffmpeg quirk — ignore exit code | Verify output exists + ffprobe |
| `No option name near 'D:'` | drive-colon path inside `-vf`/`-af` | `Set-Location "D:\youtube system\output\temp"`, use relative paths in filters |
| `ass=` file not found | wrong cwd or missing NN.ass | cd to temp\, copy ASS file into temp\ |
| Box glyphs in captions | caption font missing | `fontsdir=fonts` + montserrat-bold.ttf in temp\ |
| crop expression error | wrong formula for source ratio | Use dynamic crop formula (encoding-settings.md) |
| Filter init failed | NN/START/DUR placeholder left in | Replace ALL placeholders before running |
| Encode fails mid-clip | corrupt source segment | Re-clip with slightly different START, retry once |

## Upload Errors
| Error | Cause | Fix |
|-------|-------|-----|
| Quota exceeded | Daily limit hit | Tell user, save to upload_sheet.txt |
| Video too long | > 60s for Shorts | Trim to < 60s |
| Copyright strike | Content ID match | Tell user, review needed |
| Upload failed | Network/server | Retry once, then save to sheet |

## SEO Errors
| Error | Cause | Fix |
|-------|-------|-----|
| Score < 50 | Weak metadata | Flag for manual review |
| Title too long | > 60 chars | Auto-truncate |
| No keywords | Generic title | Add relevant keywords |

## System Errors
| Error | Cause | Fix |
|-------|-------|-----|
| FFmpeg not found | Not on PATH | Tell user to install |
| Disk space < 5GB | Storage full | Tell user to free space |
| MCP disconnected | Server crashed | Restart MCP, retry |
| Memory error | Large file | Process in segments |
| `mp.solutions` AttributeError | Newer mediapipe (1.0.1, 0.10.35) dropped legacy solutions API | Tasks API only — face_track_analyze.py already uses it |
