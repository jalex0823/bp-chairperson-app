# Chairperson Resources (PDFs)

Place all chairing-related PDF files into the `resources/pdfs` folder.

- Supported files: `.pdf`
- They will automatically appear on the Chairperson Resources page.
- These are served via the `/resources/pdfs/<filename>` route.

Environment variable used by the app:

```powershell
EXTERNAL_PDFS_DIR=c:\Temp\bp-chairperson-app\resources\pdfs
```

If deploying, set `EXTERNAL_PDFS_DIR` to a location containing your PDFs (for Heroku, include PDFs in the repo and keep this same path).
