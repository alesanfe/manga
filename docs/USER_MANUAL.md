# User Manual

This guide helps end users navigate and use the Manga Downloader application.

## Table of Contents

- [Getting Started](#getting-started)
- [User Interface](#user-interface)
- [Searching for Manga](#searching-for-manga)
- [Downloading Manga](#downloading-manga)
- [Managing Downloads](#managing-downloads)
- [Troubleshooting](#troubleshooting)

## Getting Started

### Accessing the Application

The application is accessible via web browser at:

- **Local development:** http://127.0.0.1:8000
- **Docker deployment:** http://localhost:5085
- **Production:** Contact your administrator for the production URL

### Requirements

- Modern web browser (Chrome, Firefox, Safari, Edge)
- Internet connection for downloading manga
- Sufficient disk space for downloaded files

## User Interface

### Main Navigation

The application features a clean, modern interface based on Black Dashboard theme:

- **Home:** Dashboard with quick access to features
- **Manga List:** Browse and search all available manga
- **Account:** User authentication and profile management

### Dashboard

The home page provides:
- Quick search bar
- Recently viewed manga
- Popular manga recommendations
- Download statistics

## Searching for Manga

### Basic Search

1. Navigate to the Manga List page
2. Use the search bar to find manga by title
3. Press Enter or click the search button

### Advanced Filters

Refine your search using the following filters:

- **Title:** Search by manga title
- **Genre:** Filter by one or multiple genres (Action, Adventure, Comedy, etc.)
- **Author:** Filter by author name
- **Release Year:** Filter by year range (start and end year)

### Search Tips

- Use partial titles for broader results
- Combine multiple filters for precise results
- Clear filters to see all available manga
- Use pagination to navigate through large result sets

## Downloading Manga

### Via Web Interface

1. **Find the manga:**
   - Search or browse to find your desired manga
   - Click on the manga title to view details

2. **View chapters:**
   - On the manga details page, click "View Chapters"
   - Review the list of available chapters

3. **Select chapters:**
   - Choose individual chapters or select a range
   - Click the download button

4. **Download:**
   - The application will generate a ZIP file
   - Your browser will prompt to save the file
   - The ZIP contains PDF files for each chapter

### Via API

For developers and advanced users, the API provides programmatic access:

See [API Documentation](API.md) for detailed API usage.

Basic example:
```bash
curl -X POST http://localhost:8000/api/manga/download/ \
  -H "Content-Type: application/json" \
  -d '{"manga_name": "one-piece", "chapters": [1, 10]}' \
  --output manga.zip
```

### Download Options

- **Single chapter:** Download one specific chapter
- **Chapter range:** Download a range of chapters (e.g., 1-10)
- **All chapters:** Download the complete manga series

## Managing Downloads

### Downloaded Files

- Downloads are delivered as ZIP files
- Each ZIP contains PDF files for the requested chapters
- PDF files are named according to chapter numbers

### File Organization

Recommended organization for downloaded files:

```
Downloads/
├── Manga Name/
│   ├── Chapter 1.pdf
│   ├── Chapter 2.pdf
│   └── ...
```

### Reading PDFs

Use any PDF reader to view downloaded chapters:
- Adobe Acrobat Reader
- Foxit Reader
- Sumatra PDF
- Browser built-in PDF viewers

## Troubleshooting

### Common Issues

#### Download Fails

**Problem:** Download doesn't start or fails midway

**Solutions:**
- Check your internet connection
- Ensure sufficient disk space
- Try downloading fewer chapters at a time
- Clear browser cache and try again

#### Manga Not Found

**Problem:** Search doesn't return expected results

**Solutions:**
- Check spelling of manga title
- Try partial title search
- Verify the manga is available on my.ninemanga.com
- Clear filters and search again

#### Slow Downloads

**Problem:** Downloads take longer than expected

**Solutions:**
- Download during off-peak hours
- Reduce the number of chapters per download
- Check your internet speed
- Contact administrator if issue persists

#### ZIP File Won't Open

**Problem:** Downloaded ZIP file is corrupted

**Solutions:**
- Delete the file and download again
- Check available disk space
- Try a different browser
- Ensure download completed fully

### Error Messages

| Error Message | Cause | Solution |
|---------------|-------|----------|
| "Manga not found" | Incorrect manga name | Verify spelling and try again |
| "No chapters available" | Manga has no chapters | Contact administrator |
| "Download failed" | Network or server issue | Check connection and retry |
| "Invalid request" | Incorrect API parameters | Check API documentation |

### Getting Help

If you encounter issues not covered here:

1. Check the [API Documentation](API.md) for API-related issues
2. Review the [README.md](../README.md) for setup and configuration
3. Contact your system administrator
4. Report bugs via the project's issue tracker

## Best Practices

- **Download in batches:** Download chapter ranges instead of all at once
- **Organize files:** Create folders for different manga series
- **Check disk space:** Ensure sufficient space before large downloads
- **Use stable connection:** Avoid downloading on unstable networks
- **Verify downloads:** Check that ZIP files open correctly

## Security Tips

- Only download from the official application URL
- Don't share your download links publicly
- Keep your account credentials secure
- Report suspicious activity to administrators

## Frequently Asked Questions

**Q: Can I download manga from other websites?**  
A: Currently, the application only supports my.ninemanga.com.

**Q: Is there a limit on how many chapters I can download?**  
A: No hard limit, but large downloads may take time and require significant disk space.

**Q: Can I download multiple manga at once?**  
A: Via the web interface, one download at a time. Via API, you can make multiple requests.

**Q: What format are the downloaded files?**  
A: Chapters are converted to PDF format and delivered in a ZIP archive.

**Q: Can I read manga directly in the browser?**  
A: Currently, you need to download and read the PDF files offline.

**Q: How often is the manga database updated?**  
A: Contact your administrator for update schedule information.

## Support

For additional support or questions:

- Documentation: Check the [docs](.) folder
- API Reference: See [API.md](API.md)
- Development Guide: See [DEVELOPMENT.md](DEVELOPMENT.md)
- Project Structure: See [PROJECT_STRUCTURE.md](PROJECT_STRUCTURE.md)
