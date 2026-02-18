import requests
import csv
import json
import os

seen_file = "seen_urls.json"

keywords = ["intern", 
            "internship", 
            "co-op", 
            "coop", 
            "student"]

mechanical_keywords = [
    "engineer",
    "engineering",
    "mechanical",
    "manufacturing",
    "manufacturing engineer",
    "product design",
    "design engineer",
    "mechanisms",
    "thermal",
    "fluids",
    "materials",
    "structural",
    "process engineer",
    "quality engineer",
    "test engineer",
]

mechatronics_keywords = [
    "mechatronics",
    "robotics",
    "robot",
    "controls",
    "control systems",
    "embedded",
    "hardware",
    "electromechanical",
    "automation",
    "systems integration",
]

software_keywords = [
    "software",
    "software engineer",
    "computer",
    "backend",
    "frontend",
    "full stack",
    "full-stack",
    "systems",
    "platform",
    "infrastructure",
    "developer",
    "data",
    "machine learning",
    "ml",
    "ai",
]

greenhouse_api = "https://boards-api.greenhouse.io/v1/boards/{company}/jobs"
lever_api = "https://api.lever.co/v0/postings/{company}?mode=json"

# Need function to find the internships

def is_internship(title: str) -> bool:
    title = title.lower() # Make sure titles like "Intership" or "INTERN" are still received 

    for word in keywords:
        if word in title:
            return True
    return False

def is_engineering(title: str) -> bool:
    title = title.lower()

    for word in mechanical_keywords:
        if word in title:
            return True
    
    for word in software_keywords:
        if word in title:
            return True
    
    for word in mechatronics_keywords:
        if word in title:
            return True
        
    return False

#Function to load the company names from our companies.txt file

def load_companies():
    companies = []
    file = open("companies.txt", "r")

    for line in file:
        cleaned_line = line.strip()
        if cleaned_line != "":
            companies.append(cleaned_line)

    file.close()
    
    return companies

def get_jobs(company):
    
    gh_url = greenhouse_api.format(company=company)
    r = requests.get(gh_url, timeout=20)

    if r.status_code == 200: #if works
        jobs = r.json().get("jobs", [])
        normalized = []

        for job in jobs:
            normalized.append({
                "source": "greenhouse",
                "company": company,
                "title": job.get("title", ""),
                "location": (job.get("location") or {}).get("name", ""),
                "url": job.get("absolute_url", ""),
                "updated_at": job.get("updated_at", ""),
            })

        return normalized
    
    #if greenhouse fails we try lever
    
    lever_url = lever_api.format(company=company)
    r = requests.get(lever_url, timeout=20)

    if r.status_code == 200: #if works
        jobs = r.json()
        normalized = []

        for job in jobs:
            
            title = job.get("text", "") or job.get("title", "")
            location = ""
            if isinstance(job.get("categories"), dict):
                location = job["categories"].get("location", "")
            url = job.get("applyUrl", "") or job.get("hostedUrl", "")

            normalized.append({
                "source": "lever",
                "company": company,
                "title": title,
                "location": location,
                "url": url,
                "updated_at": "",
            })

        return normalized
    
    print(f"Failed to find {company} on Greenhouse or Lever")
    return []

def load_seen_urls() -> set:
    if not os.path.exists(seen_file):
        return set()
    with open(seen_file, "r", encoding="utf-8") as f:
        return set(json.load(f))

def save_seen_urls(seen: set):
    with open(seen_file, "w", encoding="utf-8") as f:
        json.dump(sorted(list(seen)), f, indent=2)


def main():
    
    companies = load_companies()
    
    seen = load_seen_urls()
    results = []
    new_count = 0

    for company in companies:
        print(f"\n Checking {company}...")
        jobs = get_jobs(company)

        for job in jobs:
            title = job.get("title", "")
            url = job.get("url", "")

            if not url:
                continue

    # create a dictionary for the results
            if is_internship(title) and is_engineering(title):
                
                if url not in seen:
                    
                    seen.add(url)
                    new_count += 1
                    
                    results.append({
                        "source": job.get("source", ""),
                        "company": job.get("company", ""),
                        "title": job.get("title", ""),
                        "location": job.get("location", ""),
                        "url": job.get("url", ""),
                        "updated_at": job.get("updated_at", ""),
                    })

    save_seen_urls(seen)

    with open("jobs.csv", "w", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(file, fieldnames=["source", "company", "title", "location", "url", "updated_at"])

        writer.writeheader()
        writer.writerows(results)

    print(f"\nFound {new_count} NEW jobs")

if __name__ == "__main__":
    main()


    