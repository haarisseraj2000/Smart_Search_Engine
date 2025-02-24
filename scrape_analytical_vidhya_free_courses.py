from playwright.sync_api import sync_playwright
import time
import csv
import re

def scrape_analytics_vidhya_free_courses(url):
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context()
        page = context.new_page()

        page.goto(url)

        all_courses = []

        page_no = 1

        while True:

            # print(f"\nCourse No: {page_no}\n")
            
            if page.locator("#webklipper-publisher-widget-container-notification-container").is_visible():
                page.locator("#webklipper-publisher-widget-container-notification-close-div").click()

            # Wait for the course collection container to load
            page.wait_for_selector(".collections__product-cards.collections__product-cards___0b9ab")
            is_visible = page.locator("ul.products__list").locator("li").first.is_visible()

            if not is_visible:
                break

            if page.locator("#webklipper-publisher-widget-container-notification-container").is_visible():
                page.locator("#webklipper-publisher-widget-container-notification-close-div").click()
            # Extract course details on the current page
            course_items = page.locator(".products__list-item")
            for i in range(course_items.count()):
                course = course_items.nth(i)
                body = course.locator(".course-card__body")
                raw_title = body.locator("h3")
                title = raw_title.text_content().strip()
                raw_title.click()

                # extract the course link
                course_link = page.url

                # Wait for the course page to load
                time.sleep(2)  # Adjust the sleep time if necessary

                description = ""
                div_container = page.locator(".rich-text__container.rich-text__wrapper")
                # content_description_header = page.locator(".fr-view")
                # if content_description_header.is_visible():
                description = page.locator(".fr-view").nth(0).inner_text().strip()

                #Check which course dont have description
                if description == "":
                    print("\n\n----------Doesnot have Description----------\n\n")
                    print(f"Title: {title}")
                    print("\n\n")


                try:
                    course_curriculum = page.locator(".course-curriculum__container").text_content().strip()
                except Exception:
                    course_curriculum = ""


                # Step 1: Replace multiple newlines with a single space
                course_curriculum = re.sub(r"\n+", " ", course_curriculum).strip()
                description = re.sub(r"\n+", " ", description).strip()

                # Step 2: Replace multiple spaces (2 or more) with a single comma
                course_curriculum = re.sub(r" {2,}", ", ", course_curriculum)
                description = re.sub(r" {2,}", ", ", description)



                all_courses.append({"title": title, "description": description, "curriculum": course_curriculum, "course_url": course_link})
                # print(f"Title: {title}\nDescription: {description}\ncurriculum: {course_curriculum}\ncourse_url: {course_link}")

                # Go back to the course list page
                page.go_back()

                # Wait for the course list page to load
                time.sleep(2)  # Adjust the sleep time if necessary

            if page.locator("#webklipper-publisher-widget-container-notification-container").is_visible():
                page.locator("#webklipper-publisher-widget-container-notification-close-div").click()
            # Check for the next page button (icon based navigation)
            next_page_url = url + f"?page={page_no + 1}"
            page_no += 1
            page.goto(next_page_url)

        browser.close()

        # Save the course details to a CSV file
        with open("free_course_list.csv", "w", newline="", encoding="utf-8") as csvfile:
            fieldnames = ["title", "description", "curriculum", "course_url"]
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            for course in all_courses:
                writer.writerow(course)

        return all_courses

# Example usage
url = "https://courses.analyticsvidhya.com/collections"
courses = scrape_analytics_vidhya_free_courses(url)
for course in courses:
    print(course)

