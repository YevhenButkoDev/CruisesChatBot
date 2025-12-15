from playwright.sync_api import sync_playwright

def scrape_custom_dropdown(url, adults_option: int, child_option: int):
    with sync_playwright() as p:
        try:
            dropdown_selector = "#select2-countPeople_adult-container"
            browser = p.chromium.launch(headless=True)
            page = browser.new_page()

            page.goto(url)
            page.click(dropdown_selector)
            page.click(f"li.select2-results__option:has-text('{adults_option}')")
            page.wait_for_selector(".font-weight-semibold2.mt-1", state="visible")

            if child_option is not None and child_option > 0:
                page.click("#select2-countPeople_child-container")
                page.click(f"li.select2-results__option:has-text('{child_option}')")
                page.wait_for_selector(".font-weight-semibold2.mt-1", state="visible")

            # Get text from target element
            p_elements = page.query_selector_all(".font-weight-semibold2.mt-1")
            p_texts = [element.text_content().replace("\n", "").replace(" ", "").replace('\u202f', ' ') for element in p_elements]

            n_elements = page.query_selector_all(".card-title.font-weight-semibold2")
            n_texts = [element.text_content().replace("\n", "").replace('\u202f', ' ').strip() for element in n_elements]

            browser.close()

            result = [
                {"price": a, "name": b}
                for a, b in zip(p_texts, n_texts)
            ]

            return result
        except:
            return []

# Usage
if __name__ == "__main__":
    url = "https://center.cruises/cruise-booking/30948807/"
    option_selector = "2"  # Option to select

    result_html = scrape_custom_dropdown(url, option_selector)
    print(result_html)
