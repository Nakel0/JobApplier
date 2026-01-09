import json
import logging
import time
import os
import random
from pathlib import Path
from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeout

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('applications.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


def load_config():
    """Load and validate configuration file."""
    try:
        with open('config.json', 'r') as f:
            config = json.load(f)
        
        required_fields = ['companies', 'job_keywords', 'resume_path', 'your_info']
        for field in required_fields:
            if field not in config:
                raise ValueError(f"Missing required field: {field}")
        
        # Validate resume file exists
        if not os.path.exists(config['resume_path']):
            raise FileNotFoundError(f"Resume file not found: {config['resume_path']}")
        
        # Set defaults
        config.setdefault('max_applications', 10)
        config.setdefault('platforms', ['lever', 'greenhouse'])
        
        logger.info("Configuration loaded successfully")
        return config
    except FileNotFoundError:
        logger.error("config.json not found")
        raise
    except json.JSONDecodeError:
        logger.error("Invalid JSON in config.json")
        raise
    except Exception as e:
        logger.error(f"Error loading config: {str(e)}")
        raise


def load_companies_database():
    """Load companies database with career page URLs."""
    try:
        with open('companies.json', 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        logger.error("companies.json not found")
        raise
    except json.JSONDecodeError:
        logger.error("Invalid JSON in companies.json")
        raise


def human_delay(min_seconds=1, max_seconds=3):
    """Add a random human-like delay."""
    time.sleep(random.uniform(min_seconds, max_seconds))


def apply_to_lever_job(page, job_url, user_info, resume_path):
    """Apply to a job on Lever.co platform."""
    try:
        logger.info(f"Navigating to Lever job: {job_url}")
        page.goto(job_url, wait_until='domcontentloaded')
        human_delay(2, 3)
        
        # Click Apply button
        apply_selectors = [
            "a.template-btn-submit:has-text('Apply')",
            "a:has-text('Apply for this job')",
            "[data-qa='btn-apply']",
            "a.postings-btn"
        ]
        
        for selector in apply_selectors:
            try:
                apply_btn = page.locator(selector).first
                if apply_btn.is_visible(timeout=2000):
                    apply_btn.click()
                    logger.info("Clicked Apply button")
                    human_delay(2, 3)
                    break
            except Exception:
                continue
        
        # Fill application form
        try:
            # Name
            name_input = page.locator("input[name='name']").first
            if name_input.is_visible(timeout=2000):
                name_input.fill(f"{user_info['first_name']} {user_info['last_name']}")
                human_delay(0.5, 1)
        except Exception:
            pass
        
        try:
            # Email
            email_input = page.locator("input[name='email']").first
            if email_input.is_visible(timeout=2000):
                email_input.fill(user_info['email'])
                human_delay(0.5, 1)
        except Exception:
            pass
        
        try:
            # Phone
            phone_input = page.locator("input[name='phone']").first
            if phone_input.is_visible(timeout=2000):
                phone_input.fill(user_info['phone'])
                human_delay(0.5, 1)
        except Exception:
            pass
        
        try:
            # LinkedIn
            linkedin_selectors = ["input[name='urls[LinkedIn]']", "input[placeholder*='LinkedIn']"]
            for selector in linkedin_selectors:
                try:
                    linkedin_input = page.locator(selector).first
                    if linkedin_input.is_visible(timeout=1000):
                        linkedin_input.fill(user_info.get('linkedin', ''))
                        human_delay(0.5, 1)
                        break
                except Exception:
                    continue
        except Exception:
            pass
        
        try:
            # Location/City
            location_selectors = [
                "input[name='location']",
                "input[placeholder*='Location']",
                "input[placeholder*='City']"
            ]
            for selector in location_selectors:
                try:
                    loc_input = page.locator(selector).first
                    if loc_input.is_visible(timeout=1000):
                        loc_input.fill(user_info.get('location', f"{user_info.get('city', '')}, {user_info.get('state', '')}"))
                        human_delay(0.5, 1)
                        break
                except Exception:
                    continue
        except Exception:
            pass
        
        # Upload resume
        try:
            file_input = page.locator("input[type='file'][name='resume']").first
            if file_input.is_visible(timeout=2000):
                file_input.set_input_files(resume_path)
                logger.info("Resume uploaded")
                human_delay(1, 2)
        except Exception as e:
            logger.warning(f"Could not upload resume: {str(e)}")
        
        # Submit application
        try:
            submit_selectors = [
                "button[type='submit']:has-text('Submit')",
                "button.template-btn-submit",
                "button:has-text('Submit application')"
            ]
            
            for selector in submit_selectors:
                try:
                    submit_btn = page.locator(selector).first
                    if submit_btn.is_visible(timeout=2000):
                        submit_btn.click()
                        logger.info("✓ Application submitted!")
                        human_delay(2, 3)
                        return True
                except Exception:
                    continue
        except Exception as e:
            logger.warning(f"Could not submit application: {str(e)}")
        
        return False
        
    except Exception as e:
        logger.error(f"Error applying to Lever job: {str(e)}")
        return False


def apply_to_greenhouse_job(page, job_url, user_info, resume_path):
    """Apply to a job on Greenhouse.io platform."""
    try:
        logger.info(f"Navigating to Greenhouse job: {job_url}")
        page.goto(job_url, wait_until='domcontentloaded')
        human_delay(2, 3)
        
        # Click Apply button
        apply_selectors = [
            "#apply_button",
            "a#apply-button",
            "a:has-text('Apply for this job')",
            ".application-button"
        ]
        
        for selector in apply_selectors:
            try:
                apply_btn = page.locator(selector).first
                if apply_btn.is_visible(timeout=2000):
                    apply_btn.click()
                    logger.info("Clicked Apply button")
                    human_delay(2, 3)
                    break
            except Exception:
                continue
        
        # Fill application form
        try:
            # First Name
            first_name_input = page.locator("input#first_name, input[name='job_application[first_name]']").first
            if first_name_input.is_visible(timeout=2000):
                first_name_input.fill(user_info['first_name'])
                human_delay(0.5, 1)
        except Exception:
            pass
        
        try:
            # Last Name
            last_name_input = page.locator("input#last_name, input[name='job_application[last_name]']").first
            if last_name_input.is_visible(timeout=2000):
                last_name_input.fill(user_info['last_name'])
                human_delay(0.5, 1)
        except Exception:
            pass
        
        try:
            # Email
            email_input = page.locator("input#email, input[name='job_application[email]']").first
            if email_input.is_visible(timeout=2000):
                email_input.fill(user_info['email'])
                human_delay(0.5, 1)
        except Exception:
            pass
        
        try:
            # Phone Country Code dropdown (for +1) - Very important!
            phone_country_selectors = [
                "select[aria-label='Country code']",
                "select[id*='country']",
                "select[name*='phone_country']",
                "div.phone-input select",
                "div.phone-number-country-select select",
                "select[class*='country']",
                "div[data-qa='phone-country-code-input'] select"
            ]
            
            for selector in phone_country_selectors:
                try:
                    phone_country_select = page.locator(selector).first
                    if phone_country_select.is_visible(timeout=2000):
                        success = False
                        
                        # Click dropdown first to open it
                        try:
                            phone_country_select.click()
                            human_delay(0.3, 0.5)
                        except:
                            pass
                        
                        # Try multiple ways to select United States (+1)
                        try:
                            phone_country_select.select_option(label="United States (+1)")
                            logger.info("✓ Selected phone country: United States (+1)")
                            success = True
                        except:
                            try:
                                phone_country_select.select_option(label="United States")
                                logger.info("✓ Selected phone country: United States")
                                success = True
                            except:
                                try:
                                    phone_country_select.select_option(value="+1")
                                    logger.info("✓ Selected phone country code: +1")
                                    success = True
                                except:
                                    try:
                                        phone_country_select.select_option(value="1")
                                        logger.info("✓ Selected phone country code: 1")
                                        success = True
                                    except:
                                        try:
                                            phone_country_select.select_option(value="US")
                                            logger.info("✓ Selected phone country code: US")
                                            success = True
                                        except:
                                            pass
                        
                        if success:
                            human_delay(0.5, 1)
                            break
                except Exception as e:
                    logger.debug(f"Phone country selector {selector} failed: {str(e)}")
                    continue
        except Exception as e:
            logger.warning(f"⚠️  Could not select phone country code: {str(e)}")
        
        try:
            # Phone number (without country code)
            phone_input = page.locator("input#phone, input[name='job_application[phone]']").first
            if phone_input.is_visible(timeout=2000):
                phone_input.fill(user_info['phone'])
                logger.info(f"Filled phone: {user_info['phone']}")
                human_delay(0.5, 1)
        except Exception:
            pass
        
        try:
            # City field - Specific targeting
            city_selectors = [
                "input[name='job_application[city]']",
                "input#city",
                "input[name*='city']",
                "input[placeholder*='City']",
                "input[placeholder*='city']",
                "input[aria-label*='City']",
                "input[aria-label*='city']"
            ]
            for selector in city_selectors:
                try:
                    city_input = page.locator(selector).first
                    if city_input.is_visible(timeout=2000):
                        city_input.fill(user_info.get('city', 'Landover'))
                        logger.info(f"✓ Filled city: {user_info.get('city', 'Landover')}")
                        human_delay(0.5, 1)
                        break
                except Exception as e:
                    logger.debug(f"City selector {selector} failed: {str(e)}")
                    continue
        except Exception as e:
            logger.debug(f"Could not fill city: {str(e)}")
        
        try:
            # State field
            state_selectors = [
                "input[name='job_application[state]']",
                "input#state",
                "input[name*='state']",
                "input[placeholder*='State']",
                "input[placeholder*='state']",
                "select[name*='state']",
                "select#state"
            ]
            for selector in state_selectors:
                try:
                    state_input = page.locator(selector).first
                    if state_input.is_visible(timeout=2000):
                        # Check if it's a select or input
                        tag_name = state_input.evaluate("el => el.tagName")
                        if tag_name.lower() == "select":
                            # Try to select by label or value
                            try:
                                state_input.select_option(label=user_info.get('state', 'Maryland'))
                            except:
                                try:
                                    state_input.select_option(value=user_info.get('state', 'Maryland'))
                                except:
                                    state_input.select_option(value="MD")
                            logger.info(f"✓ Selected state: {user_info.get('state', 'Maryland')}")
                        else:
                            state_input.fill(user_info.get('state', 'Maryland'))
                            logger.info(f"✓ Filled state: {user_info.get('state', 'Maryland')}")
                        human_delay(0.5, 1)
                        break
                except Exception as e:
                    logger.debug(f"State selector {selector} failed: {str(e)}")
                    continue
        except Exception as e:
            logger.debug(f"Could not fill state: {str(e)}")
        
        try:
            # Zip Code field
            zip_selectors = [
                "input[name='job_application[zip]']",
                "input[name='job_application[zip_code]']",
                "input#zip",
                "input#zip_code",
                "input[name*='zip']",
                "input[placeholder*='Zip']",
                "input[placeholder*='zip']"
            ]
            for selector in zip_selectors:
                try:
                    zip_input = page.locator(selector).first
                    if zip_input.is_visible(timeout=2000):
                        zip_input.fill(user_info.get('zip_code', '20785'))
                        logger.info(f"✓ Filled zip code: {user_info.get('zip_code', '20785')}")
                        human_delay(0.5, 1)
                        break
                except Exception as e:
                    logger.debug(f"Zip selector {selector} failed: {str(e)}")
                    continue
        except Exception as e:
            logger.debug(f"Could not fill zip code: {str(e)}")
        
        try:
            # General Location field (fallback for single location field)
            location_selectors = [
                "input[name='job_application[location]']",
                "input#location",
                "input[placeholder*='location']",
                "input[placeholder*='Location']",
                "input[aria-label*='Location']"
            ]
            for selector in location_selectors:
                try:
                    loc_input = page.locator(selector).first
                    if loc_input.is_visible(timeout=2000):
                        # Use full location or city, state
                        full_location = user_info.get('location', f"{user_info.get('city', 'Landover')}, {user_info.get('state', 'Maryland')}")
                        loc_input.fill(full_location)
                        logger.info(f"✓ Filled location: {full_location}")
                        human_delay(1, 2)
                        break
                except Exception as e:
                    logger.debug(f"Location selector {selector} failed: {str(e)}")
                    continue
        except Exception as e:
            logger.debug(f"Could not fill location: {str(e)}")
        
        try:
            # Country dropdown - Very important for Greenhouse (for location/address)
            country_selectors = [
                "select[name='job_application[country]']",
                "select#country",
                "select[name*='country']",
                "select[aria-label*='Country']",
                "div[data-qa='country-input'] select"
            ]
            
            for selector in country_selectors:
                try:
                    country_select = page.locator(selector).first
                    if country_select.is_visible(timeout=2000):
                        # Try multiple ways to select United States
                        success = False
                        try:
                            country_select.select_option(label="United States")
                            logger.info("✓ Selected country: United States")
                            success = True
                        except:
                            try:
                                country_select.select_option(value="United States")
                                logger.info("✓ Selected country: United States (by value)")
                                success = True
                            except:
                                try:
                                    country_select.select_option(value="US")
                                    logger.info("✓ Selected country: US")
                                    success = True
                                except:
                                    try:
                                        country_select.select_option(value="USA")
                                        logger.info("✓ Selected country: USA")
                                        success = True
                                    except:
                                        pass
                        
                        if success:
                            human_delay(0.5, 1)
                            break
                except Exception as e:
                    logger.debug(f"Country selector {selector} failed: {str(e)}")
                    continue
        except Exception as e:
            logger.warning(f"⚠️  Could not select country: {str(e)}")
        
        # Upload resume
        try:
            file_input = page.locator("input[type='file'][name='resume'], input[type='file']#resume").first
            if file_input.is_visible(timeout=2000):
                file_input.set_input_files(resume_path)
                logger.info("Resume uploaded")
                human_delay(1, 2)
        except Exception as e:
            logger.warning(f"Could not upload resume: {str(e)}")
        
        # Submit application
        try:
            submit_selectors = [
                "input[type='submit'][value='Submit Application']",
                "button[type='submit']:has-text('Submit')",
                "#submit_app"
            ]
            
            for selector in submit_selectors:
                try:
                    submit_btn = page.locator(selector).first
                    if submit_btn.is_visible(timeout=2000):
                        submit_btn.click()
                        logger.info("✓ Application submitted!")
                        human_delay(2, 3)
                        return True
                except Exception:
                    continue
        except Exception as e:
            logger.warning(f"Could not submit application: {str(e)}")
        
        return False
        
    except Exception as e:
        logger.error(f"Error applying to Greenhouse job: {str(e)}")
        return False


def search_company_jobs(page, company_url, platform, keywords, company_name):
    """Search for jobs at a company matching keywords."""
    try:
        page.goto(company_url, wait_until='domcontentloaded')
        human_delay(2, 3)
        
        # Take screenshot for debugging
        screenshot_path = f"company_{company_name}_{platform}.png"
        page.screenshot(path=screenshot_path)
        logger.info(f"📸 Screenshot saved: {screenshot_path}")
        
        matching_jobs = []
        
        if platform == 'lever':
            # Get all job postings on Lever
            job_posting_selectors = [
                "div.posting",
                "a.posting",
                "div[class*='posting']",
                "a[class*='posting']"
            ]
            
            job_postings = []
            for selector in job_posting_selectors:
                job_postings = page.locator(selector).all()
                if len(job_postings) > 0:
                    logger.info(f"Found {len(job_postings)} job elements with selector: {selector}")
                    break
            
            logger.info(f"Checking {len(job_postings)} job postings for keyword matches...")
            
            for posting in job_postings:
                try:
                    # Try multiple selectors for title
                    title = ""
                    title_selectors = [
                        "h5[data-qa='posting-name']",
                        ".posting-title",
                        "h5",
                        "h4",
                        "a"
                    ]
                    
                    for sel in title_selectors:
                        try:
                            title_elem = posting.locator(sel).first
                            title = title_elem.text_content().strip()
                            if title and len(title) > 0:
                                break
                        except:
                            continue
                    
                    if not title:
                        continue
                    
                    logger.debug(f"Checking job: {title}")
                    
                    # Check if any keyword matches
                    title_lower = title.lower()
                    if any(keyword.lower() in title_lower for keyword in keywords):
                        # Get job URL
                        job_url = None
                        try:
                            link_elem = posting.locator("a").first
                            job_url = link_elem.get_attribute('href')
                            
                            if job_url and not job_url.startswith('http'):
                                job_url = company_url + job_url
                        except:
                            # If posting itself is a link
                            job_url = posting.get_attribute('href')
                            if job_url and not job_url.startswith('http'):
                                job_url = company_url + job_url
                        
                        if job_url:
                            matching_jobs.append({
                                'title': title,
                                'url': job_url,
                                'platform': 'lever'
                            })
                            logger.info(f"✓ Match found: {title}")
                except Exception as e:
                    logger.debug(f"Error processing posting: {str(e)}")
                    continue
        
        elif platform == 'greenhouse':
            # Get all job postings on Greenhouse
            job_selectors = [
                "div.opening",
                "section.level-0",
                "div[class*='job']",
                "div[class*='opening']",
                "a[href*='/jobs/']",
                "section"
            ]
            
            job_postings = []
            for selector in job_selectors:
                job_postings = page.locator(selector).all()
                if len(job_postings) > 0:
                    logger.info(f"Found {len(job_postings)} job elements with selector: {selector}")
                    break
            
            logger.info(f"Checking {len(job_postings)} job postings for keyword matches...")
            
            for posting in job_postings:
                try:
                    # Try to get title and link
                    title = ""
                    job_url = None
                    
                    # Try finding link with title
                    link_elem = posting.locator("a").first
                    if link_elem.is_visible(timeout=1000):
                        title = link_elem.text_content().strip()
                        job_url = link_elem.get_attribute('href')
                    
                    if not title:
                        continue
                    
                    logger.debug(f"Checking job: {title}")
                    
                    # Check if any keyword matches
                    title_lower = title.lower()
                    if any(keyword.lower() in title_lower for keyword in keywords):
                        # Fix URL if relative
                        if job_url and not job_url.startswith('http'):
                            if job_url.startswith('/'):
                                base_url = '/'.join(company_url.split('/')[:3])
                                job_url = base_url + job_url
                            else:
                                job_url = company_url + '/' + job_url
                        
                        if job_url:
                            matching_jobs.append({
                                'title': title,
                                'url': job_url,
                                'platform': 'greenhouse'
                            })
                            logger.info(f"✓ Match found: {title}")
                except Exception as e:
                    logger.debug(f"Error processing posting: {str(e)}")
                    continue
        
        # Remove duplicate jobs based on URL
        seen_urls = set()
        unique_jobs = []
        for job in matching_jobs:
            if job['url'] not in seen_urls:
                seen_urls.add(job['url'])
                unique_jobs.append(job)
        
        return unique_jobs
        
    except Exception as e:
        logger.error(f"Error searching company jobs: {str(e)}")
        return []


def main():
    """Main application logic."""
    try:
        # Load configuration
        config = load_config()
        companies_db = load_companies_database()
        
        companies = config['companies']
        keywords = config['job_keywords']
        platforms = config['platforms']
        resume_path = config['resume_path']
        user_info = config['your_info']
        max_applications = config['max_applications']
        
        logger.info("=" * 70)
        logger.info("🎯 Company Career Page Job Application Bot")
        logger.info("=" * 70)
        logger.info(f"Companies to target: {', '.join(companies)}")
        logger.info(f"Job keywords: {', '.join(keywords)}")
        logger.info(f"Platforms: {', '.join(platforms)}")
        logger.info(f"Max applications: {max_applications}")
        logger.info("=" * 70 + "\n")
        
        # Initialize Playwright
        with sync_playwright() as p:
            # Launch browser
            browser = p.chromium.launch(
                headless=False,
                args=['--disable-blink-features=AutomationControlled']
            )
            
            context = browser.new_context(
                user_agent='Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                viewport={'width': 1920, 'height': 1080}
            )
            
            page = context.new_page()
            
            # Remove webdriver flag
            page.add_init_script("""
                Object.defineProperty(navigator, 'webdriver', {
                    get: () => undefined
                });
            """)
            
            applications_count = 0
            
            # Loop through each company
            for company in companies:
                if applications_count >= max_applications:
                    logger.info(f"Reached maximum applications limit: {max_applications}")
                    break
                
                # Find company in database
                company_url = None
                platform = None
                
                for plat in platforms:
                    if plat in companies_db and company in companies_db[plat]:
                        company_url = companies_db[plat][company]
                        platform = plat
                        break
                
                if not company_url:
                    logger.warning(f"❌ Company '{company}' not found in database. Skipping...")
                    continue
                
                logger.info(f"\n{'='*70}")
                logger.info(f"🏢 Searching {company.upper()} ({platform})")
                logger.info(f"{'='*70}")
                
                # Search for matching jobs
                matching_jobs = search_company_jobs(page, company_url, platform, keywords, company)
                
                logger.info(f"Found {len(matching_jobs)} matching jobs")
                
                # Apply to matching jobs
                for job in matching_jobs:
                    if applications_count >= max_applications:
                        logger.info(f"Reached maximum applications limit: {max_applications}")
                        break
                    
                    logger.info(f"\n📋 Job: {job['title']}")
                    logger.info(f"🔗 URL: {job['url']}")
                    
                    # Apply based on platform
                    success = False
                    if job['platform'] == 'lever':
                        success = apply_to_lever_job(page, job['url'], user_info, resume_path)
                    elif job['platform'] == 'greenhouse':
                        success = apply_to_greenhouse_job(page, job['url'], user_info, resume_path)
                    
                    if success:
                        applications_count += 1
                        logger.info(f"✓ Successfully applied! ({applications_count}/{max_applications})")
                    else:
                        logger.info(f"✗ Application failed or incomplete")
                    
                    # Delay between applications
                    human_delay(3, 5)
            
            logger.info(f"\n{'='*70}")
            logger.info(f"🎉 Application session completed!")
            logger.info(f"📊 Total applications: {applications_count}")
            logger.info(f"{'='*70}\n")
            
            # Close browser
            browser.close()
            
    except KeyboardInterrupt:
        logger.info("Application interrupted by user")
    except Exception as e:
        logger.error(f"Fatal error: {str(e)}")
        raise


if __name__ == "__main__":
    main()
