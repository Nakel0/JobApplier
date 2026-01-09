# JobApplier

Automated job application system that applies directly to company career pages (Lever, Greenhouse) using Python and Playwright.

## Why This Approach?

Traditional job boards (Indeed, LinkedIn, ZipRecruiter) have aggressive bot detection and CAPTCHAs. This tool takes a different approach:

✅ **Targets company career pages directly** (Lever.co, Greenhouse.io)  
✅ **No CAPTCHA issues** - Company career pages rarely have bot detection  
✅ **Better success rate** - Direct employer applications  
✅ **Consistent structure** - Each platform has predictable forms  
✅ **Quality companies** - Target specific employers you want  

## Setup

1. Install dependencies:
```bash
pip install -r requirements.txt
playwright install chromium
```

2. Configure your information in `config.json`:
```json
{
  "companies": ["stripe", "shopify", "github", "cloudflare"],
  "job_keywords": ["devops", "sre", "cloud engineer"],
  "platforms": ["lever", "greenhouse"],
  "resume_path": "resume.pdf",
  "your_info": {
    "first_name": "John",
    "last_name": "Doe",
    "email": "john.doe@example.com",
    "phone": "555-123-4567",
    "linkedin": "https://linkedin.com/in/johndoe",
    "location": "Maryland, USA"
  },
  "max_applications": 10
}
```

3. Update your personal information with real details

4. Place your resume PDF in the project directory

## Usage

Run the application:
```bash
python3 app.py
```

The bot will:
1. Visit each company's career page (from `companies.json` database)
2. Search for jobs matching your keywords
3. For each matching job:
   - Open the job posting
   - Click Apply
   - Fill in your personal information
   - Upload your resume
   - Submit the application
4. Log all attempts to `applications.log`
5. Stop after reaching max_applications

## Supported Companies

The `companies.json` file contains pre-configured career page URLs for popular tech companies.

### Lever.co Companies (10+ included)
- Stripe, Shopify, GitHub, Cloudflare, HashiCorp, Docker, Netlify, Twitch, Figma, Canva, etc.

### Greenhouse.io Companies (10+ included)
- Datadog, GitLab, Airbnb, DoorDash, Snap, Lyft, Robinhood, Coinbase, Notion, Dropbox, etc.

## Adding More Companies

To add a company:

1. Find their career page
2. Identify the platform (Lever or Greenhouse)
3. Add to `companies.json`:

```json
{
  "lever": {
    "company-name": "https://jobs.lever.co/company-name"
  },
  "greenhouse": {
    "company-name": "https://boards.greenhouse.io/company-name"
  }
}
```

4. Add the company name to your `config.json` companies list

## Configuration Options

- `companies`: List of company names to apply to (must exist in companies.json)
- `job_keywords`: Keywords to search for in job titles (e.g., "devops", "sre")
- `platforms`: Which platforms to use ["lever", "greenhouse"]
- `resume_path`: Path to your resume PDF file
- `your_info`: Your personal information for applications
  - `first_name`, `last_name`: Your full name
  - `email`: Your email address
  - `phone`: Your phone number
  - `linkedin`: Your LinkedIn profile URL (optional)
  - `location`: Your location (optional)
- `max_applications`: Maximum number of applications per run

## How It Works

### Lever.co Applications
1. Visits company's Lever career page
2. Finds jobs matching keywords
3. Clicks "Apply for this job"
4. Fills form fields: name, email, phone, LinkedIn
5. Uploads resume
6. Submits application

### Greenhouse.io Applications
1. Visits company's Greenhouse career page
2. Finds jobs matching keywords
3. Clicks "Apply for this job"
4. Fills form fields: first name, last name, email, phone
5. Uploads resume
6. Submits application

## Benefits Over Job Boards

| Feature | Job Boards (Indeed/LinkedIn) | Company Career Pages |
|---------|------------------------------|---------------------|
| CAPTCHA Issues | ❌ Frequent | ✅ Rare/None |
| Bot Detection | ❌ Aggressive | ✅ Minimal |
| Success Rate | ❌ Low | ✅ High |
| Direct to Employer | ❌ No | ✅ Yes |
| Form Consistency | ❌ Variable | ✅ Predictable |

## Notes

- The browser runs in visible mode so you can see the automation
- All applications are logged to `applications.log` with timestamps
- The bot uses human-like delays between actions
- Some companies may have additional questions beyond basic fields - these will be skipped
- The bot only applies to jobs that match your keywords
- Screenshots are NOT taken by default (unlike the job board version)

## Troubleshooting

**No matching jobs found?**
- Check that your keywords match actual job titles
- Try broader keywords like "engineer" instead of "devops engineer"

**Form fields not filling?**
- Some companies have custom form fields
- Check the logs to see what failed
- The bot will still attempt to submit if resume is uploaded

**Applications not submitting?**
- Some companies have mandatory fields beyond the basics
- Check if there's a confirmation page (usually means success)
- Review `applications.log` for details

## Example Run

```
🎯 Company Career Page Job Application Bot
Companies to target: stripe, shopify, github
Job keywords: devops, sre, cloud engineer
Platforms: lever, greenhouse
Max applications: 10

🏢 Searching STRIPE (lever)
Found 3 matching jobs

📋 Job: Senior DevOps Engineer
✓ Successfully applied! (1/10)

📋 Job: Site Reliability Engineer
✓ Successfully applied! (2/10)

🎉 Application session completed!
📊 Total applications: 2
```

## Privacy & Ethics

- This tool automates form filling, not deception
- It submits real applications with your real information
- Use responsibly and only apply to jobs you're actually interested in
- Respect companies' application policies
- Don't spam applications

## License

MIT License - Use at your own risk
