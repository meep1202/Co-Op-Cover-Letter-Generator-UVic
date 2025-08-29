'''
July 8th, 2025
Hayden Fee
Co-Op Cover Letter Generator
'''
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
import time
import datetime
import os
import fpdf

# Define driver path
path = "driver/chromedriver.exe"
cservice = Service(executable_path=path)
options = webdriver.ChromeOptions()
options.add_experimental_option('excludeSwitches', ['enable-logging']) # Silences log
options.add_argument("--log-level=3") # Silences log
#options.add_argument("--headless=new") # Removes visibility

# Define date
date = datetime.datetime.now().strftime("%B %d, %Y") # Month day, year

# Define color codes
GREEN = '\033[92m'
RESET = '\033[0m' # Resets color to default

def duo(driver, fromgenerate):
    # Selects other options when presented with duo wait screen
    otheroptions = WebDriverWait(driver, 120).until(EC.presence_of_element_located(("link text", "Other options")))
    time.sleep(0.5)
    otheroptions.click()

    print(f"{GREEN}Bypassing 2FA\n{RESET}")

    # Selects use bypass code instead of 2fa
    usecode = WebDriverWait(driver, 60).until(EC.presence_of_element_located(("css selector", '[data-testid="test-id-bypass"]')))
    time.sleep(0.5)
    usecode.click()

    # Enters bypass code
    codeinput = WebDriverWait(driver, 60).until(EC.presence_of_element_located(("id", "passcode-input")))
    time.sleep(0.5)
    codeinput.send_keys(ReturnBypassCode(fromgenerate))

    # If setting is 0 or 2, selects trust browser
    if fromgenerate != 1:
        trust = WebDriverWait(driver, 60).until(EC.presence_of_element_located(("id", "trust-browser-button")))
        time.sleep(0.5)
        trust.click()
    print(f"{GREEN}2FA Bypassed\n{RESET}")


def login(driver):
    # Reads username
    userfile = open("userinfo/username.txt", "r")
    u = userfile.read()
    userfile.close()

    if u.lower() != "manual":
        # Reads password
        passfile = open("userinfo/password.txt", "r")
        p = passfile.read()
        passfile.close()

        # Enters username
        username = WebDriverWait(driver, 60).until(EC.presence_of_element_located(("id", "username")))
        time.sleep(0.5)
        username.send_keys(u)

        # Enters password
        password = WebDriverWait(driver, 60).until(EC.presence_of_element_located(("id", "password")))
        time.sleep(0.5)
        password.send_keys(p)

        # Submits login info
        submit = driver.find_element("name", "submitBtn")
        submit.click()
    else:
        print(f"{GREEN}Log in\n{RESET}")


def GenerateBypassCodes(): # Uses 2 bypass codes and generates 10 new ones
    # Initializes driver
    driver = webdriver.Chrome(service=cservice, options=options)

    # Goes to mfa management site
    url = "https://www.uvic.ca/netlink/manage/mfa/regenerateDuoBypassCodes"
    driver.get(url)

    # Logs in
    login(driver)
    duo(driver, 2)
    duo(driver, 1)

    # Selects 10 bypass code generation
    generateoption = WebDriverWait(driver, 60).until(EC.presence_of_element_located(("id", "single")))
    time.sleep(0.5)
    generateoption.click()

    # Generates codes
    submit = driver.find_element("id", "submit")
    submit.click()

    # Waits for loading
    WebDriverWait(driver, 60).until(EC.presence_of_element_located(("link text", "list-group-item")))
    time.sleep(0.5)

    # Selects codes and adds them to list
    codeids = driver.find_elements("class name", "list-group-item")
    codes = []
    for codeid in codeids[:-1]:
        codes.append(codeid.text + "\n")
    codes.append(codeids[-1])

    # Closes driver
    driver.quit()

    # Adds codes to file
    codefile = open("maintenance/codes.txt", "w")
    for line in codes:
        codefile.write(line)
    codefile.close()


def ReturnBypassCode(fromgenerate): # Returns one bypass code and removes it from the codes file. if less than 3 codes remaining, generate new codes and select one.
    # Reads all codes
    codefile = open("maintenance/codes.txt", "r")
    codes = []
    for line in codefile:
        codes.append(line)
    codefile.close()

    # If less than 3 codes, generates more
    if len(codes) <= 3:
        if fromgenerate == 0:
            GenerateBypassCodes()
        codefile = open("maintenance/codes.txt", "r")
        codes = []
        for line in codefile:
            codes.append(line)
        codefile.close()

    # Rewrites existing codes without the one used
    codefile = open("maintenance/codes.txt", "w")
    for code in codes[1:]:
        codefile.write(code)
    codefile.close()

    # Returns used code
    return codes[0]


def SetupGenerateCodes():
    print(f"{GREEN}\n\n\n\n\n\nNo bypass codes have been generated yet, so you'll need to use two factor authentication this one time\nThe program will automatically sign in using your netlink id and password, but you'll need to be quick with Duo 2FA\nA duo prompt will come up. You'll have one minute to fulfill it with 2fa. Then another prompt will come up. Fulfill it with 2fa, then don't touch anything.\nYou may need to open the app itself if the notifications aren't working\n{RESET}")
    g = input(f"{GREEN}\nPress enter once you've prepared your Duo 2FA device\n{RESET}")

    # Initializes driver
    driver = webdriver.Chrome(service=cservice, options=options)

    # Goes to mfa management site
    url = "https://www.uvic.ca/netlink/manage/mfa/regenerateDuoBypassCodes"
    driver.get(url)

    # Logs in
    login(driver)

    time.sleep(1)
    print(f"{GREEN}Confirm first now{RESET}")

    # Trusts browser
    trust = WebDriverWait(driver, 60).until(EC.presence_of_element_located(("id", "trust-browser-button")))
    trust.click()

    print(f"{GREEN}Confirmed first\n{RESET}")

    time.sleep(1)
    print(f"{GREEN}Confirm second now{RESET}")

    # Selects 10 bypass code generation
    generateoption = WebDriverWait(driver, 60).until(EC.presence_of_element_located(("id", "single")))
    time.sleep(0.5)
    generateoption.click()

    print(f"{GREEN}Confirmed second{RESET}")

    # Generates codes
    submit = driver.find_element("id", "submit")
    submit.click()

    # Waits for loading
    WebDriverWait(driver, 60).until(EC.presence_of_element_located(("class name", "list-group-item")))
    time.sleep(0.5)

    # Selects codes and adds them to list
    codeids = driver.find_elements("class name", "list-group-item")
    codes = []
    for codeid in codeids[:-1]:
        codes.append(codeid.text + "\n")
    codes.append(codeids[-1].text)
    
    # Closes driver
    driver.quit()

    # Adds codes to file
    codefile = open("maintenance/codes.txt", "w")
    for line in codes:
        codefile.write(line)
    codefile.close()


def SetupAddParagraphs(keywordfile, paragraphfile, keyempty): # Prompts user to input keywords and paragraphs, then writes them to files
    keyparagraph = ""
    while keyparagraph != "!q":
        keyparagraph = input(f"{GREEN}\n\n\n\n\n\n\n\n\n\nPlease enter a keyword or keywords, separated by semicolons, as well as the paragraph corresponding to that/those keyword(s), separated from the keywords by a | (vertical line).\nDo not use any spaces or tabs in keywords unless you want a keyword with multiple words (E.g. Biochemical Engineering).\nParagraphs appear in the order you enter them here, and without duplicates\nKeywords are not case sensitive\nYou may use '{{0}}' to refer to the job title, '{{1}}' to refer to the organization name, '{{2}}' to insert an enter/return, and '{{3}}' to insert today's date\nOnce you are finished with a keyword-paragraph combination, press enter. Once you are finished adding keywords and paragraphs, type '!q'\nIf you would like an example, type '!e'\n\n{RESET}")
        if keyparagraph == "!e":
            print(f"{GREEN}\n\n\n\n\n\n\n\n\n\nbiochem;biochemical;biochemical engineering;keywords|This is a paragraph corresponding to biochemical engineering.{{2}}Today is {{3}}{{2}}Thank you to the organization {{1}} for giving me the job title of {{0}}\n{RESET}")
            time.sleep(2.5)
            keyparagraph = input(f"{GREEN}Press enter to continue, or type '!q' and enter to quit\n{RESET}")
        elif keyparagraph != "!q":
            if '|' not in keyparagraph:
                print(f"{GREEN}Must include '|'\n{RESET}")
            else:
                split = keyparagraph.split("|")
                if keyempty is True:
                    keywordfile.write(split[0])
                    keyempty = False
                else:
                    keywordfile.write("\n" + split[0])
                paragraphfile.write("\n" + split[1])
        time.sleep(1)


def Setup():
    # Gets username and adds to file
    usernamefile = open("userinfo/username.txt", "r+")
    username = usernamefile.read().strip()
    if username == "":
        username = input(f"{GREEN}Please enter netlink username. If wanting to enter username and password manually, enter 'manual':\n\t{RESET}").strip()
        usernamefile.write(username)
    usernamefile.close()

    time.sleep(1)

    if username.lower() != "manual":
        # Gets password and adds to file
        passwordfile = open("userinfo/password.txt", "r+")
        password = passwordfile.read().strip()
        if password == "":
            password = input(f"{GREEN}Please enter netlink password:\n\t{RESET}").strip()
            passwordfile.write(password)
        passwordfile.close()

        # Removes visibility and manual option for password entry
        options.add_argument("--headless=new")

        time.sleep(1)

    # Gets target year and season and adds them to file
    extrainfofile = open("coverletterinfo/extrainfo.txt", "r+")
    year = extrainfofile.readline().strip()
    season = extrainfofile.readline().strip()
    if year == "":
        year = input(f"{GREEN}Please enter targeted Co-Op year: (E.g. 2026)\n\t{RESET}").strip()
        extrainfofile.write(year + "\n")
    if season == "":
        season = input(f"{GREEN}Please enter targeted Co-Op season: (Fall, Spring, or Summer)\n\t{RESET}").strip().title()
        extrainfofile.write(season)
    extrainfofile.close()

    time.sleep(1)

    # Gets opening and closing paragraph
    paragraphfile = open("coverletterinfo/paragraphs.txt", "r")
    keyparagraph = paragraphfile.read()
    paragraphfile.close()
    paragraphfile = open("coverletterinfo/paragraphs.txt", "a")
    if keyparagraph == "":
        paragraphfile.write(input(f"{GREEN}Enter opening paragraph. You may use '{{0}}' to refer to the job title, '{{1}}' to refer to the organization name, {{2}} as enters/returns, and {{3}} for today's date\n{RESET}"))
        paragraphfile.write("\n" + input(f"{GREEN}Enter closing paragraph. You may use '{{0}}' to refer to the job title, '{{1}}' to refer to the organization name, {{2}} as enters/returns, and {{3}} for today's date\n{RESET}"))

    time.sleep(1)

    # If no keywords or wants to add more paragraphs, calls SetupAddParagraphs
    keywordfile = open("coverletterinfo/keywords.txt", "r")
    x = keywordfile.read()
    keywordfile.close()
    keywordfile = open("coverletterinfo/keywords.txt", "a")
    if x != "":
        x = input(f"{GREEN}Would you like to add more keywords and paragraphs? Enter 'Y' (case insensitive) for yes and anything else for no\n{RESET}").lower()
        if x == "y":
            SetupAddParagraphs(keywordfile, paragraphfile, False)
    else:
        SetupAddParagraphs(keywordfile, paragraphfile, True)
    keywordfile.close()
    paragraphfile.close()

    time.sleep(1)

    keysfile = open("maintenance/keys.txt", "r")
    x = keysfile.read()
    keysfile.close()

    if x != "":
        x = input(f"{GREEN}Would you like to reset stored keys? This will make a new cover letter for each available Co-Op. Keep in mind this will overwrite the old cover letters if they are created on the same day.\nThis should likely only be done if you've changed or added any keyword or paragraph\nEnter 'Y' (case insensitive) for yes and anything else for no\n{RESET}").lower()
        if x == "y":
            keysfile = open("maintenance/keys.txt", "w")
            keysfile.close()
            time.sleep(0.5)
            print(f"\n{GREEN}Resetting keys{RESET}")

    time.sleep(1)

    # If less than or equal to 2 codes, calls SetupGenerateCodes
    codefile = open("maintenance/codes.txt", "r")
    x = codefile.read()
    if len(x) <= 19:
        SetupGenerateCodes()
    
    time.sleep(1)

    # Yaps
    print(f"{GREEN}\nUsername and password can be edited from the folder userinfo, while season, year, keywords, and paragraphs can be edited from the folder coverletterinfo\n{RESET}")
    time.sleep(1.5)
    print(f"{GREEN}If you change keywords or paragraphs AT ALL, it is a good idea to clear the keys file in the maintenance folder (without deleting the file). Keep in mind this will recreate any previously created cover letters in a later dated folder, or overwrite them if the date is the same\n{RESET}")
    time.sleep(1.5)
    print(f"{GREEN}Make sure you have access to the specific UVic Co-Op season\n{RESET}")
    time.sleep(1.5)
    print(f"{GREEN}If there are any bugs or errors, please report them here: https://forms.gle/p8X8zCwHLGct85fY8\n\n{RESET}")
    time.sleep(1.5)
    

def Scraper():
    # Initializes driver
    driver = webdriver.Chrome(service=cservice, options=options)

    # Go to login
    url = "https://learninginmotion.uvic.ca/students/NetlinkID/student-login.htm"
    driver.get(url)

    print(f"{GREEN}\n\nLogging in. Please DO NOT accept or deny any duo notifications.\n\n{RESET}")
    # Log in
    login(driver)
    duo(driver, 2)

    time.sleep(10)

    # Go to the job postings site
    url = "https://learninginmotion.uvic.ca/myAccount/co-op/postings.htm"
    driver.get(url)

    # Grab year and season
    extrainfofile = open("coverletterinfo/extrainfo.txt", "r")
    year = extrainfofile.readline().strip()
    season = extrainfofile.readline().strip()
    extrainfofile.close()

    time.sleep(10)

    # Choose specific job posting based on year and season
    try:
        seasonbutton = driver.find_element("link text", "{0} - {1} - all jobs open to me".format(year, season))
    except:
        seasonbutton = driver.find_element("link text", "{0} - {1} - all posting open to me".format(year, season))
    seasonbutton.click()

    time.sleep(5)

    # get all rows of posting table
    rows = driver.find_elements("tag name", "tr")

    cells = []

    # get all cells of posting table
    for row in rows:
        if "posting" in row.get_attribute("id"):
            cells.append(row.find_elements("tag name", "td"))

    links = []
    setkeys = set()

    # Get keys from a file
    keysfile = open("maintenance/keys.txt", "r")
    for line in keysfile:
        setkeys.add(line.strip())
    keysfile.close()

    # Add new keys to same file
    keysfile = open("maintenance/keys.txt", "a")
    for celllist in cells:
        if celllist[3].get_attribute("data-totitle") + "," + celllist[4].find_element("tag name", "span").text not in setkeys:
            keysfile.write(celllist[3].get_attribute("data-totitle") + "," + celllist[4].find_element("tag name", "span").text + "\n")
            links.append(celllist[3].find_elements("tag name", "span")[-1].find_element("tag name", "a"))
    keysfile.close()

    labels = {
        "Job Title:": 0,
        "Organization Name": 1,
        "If by Website, go to:": 2,
        "If by Email, send to:": 2,
        "Job Location:": 3,
        "Application Deadline:": 4,
        "Co-op Work term Duration:": 5,
        "Are remote work arrangements possible for this co-op role?:": 6,
        "Salary/Wage:": 7,
        "Job Description:": 8,
        "Qualifications:": 9
    }

    print(f"{GREEN}\n\nHarvesting information of postings and making cover letters:{RESET}")
    print(f"{GREEN}" + "0/" + str(len(links)) + f"{RESET}")
    info = []
    for i, link in enumerate(links):
        # Open every posting
        link.click()
        driver.switch_to.window(driver.window_handles[-1])

        notload = True
        while notload:
            try:
                posting = WebDriverWait(driver, 60).until(EC.presence_of_element_located(("id", "postingDiv")))
                notload = False
            except:
                driver.refresh()

        time.sleep(0.5)
        #posting = driver.find_element("id", "postingDiv")
        rows = posting.find_elements("tag name", "tr")

        # Create empty info array
        info.append([])
        for o in range(10):
            info[i].append([o])

        # Harvest info
        for row in rows:
            if any(row.find_elements("tag name", "td")[0].text == key for key in labels.keys()):
                info[i][labels[row.find_elements("tag name", "td")[0].text]] = row.text

        # Clean file name
        filename = "".join(c for c in info[i][0] + ", " + info[i][1] if c.isalnum() or c in (',', ' ', '_', '-')).strip() # Removes non valid characters
        filename = filename.replace("Organization Name ", "") # Removes Organization Name
        filename = filename[10:] # Removes "Job Title:" 

        # Create folder based on date
        os.makedirs("output/" + date + "/" + filename, exist_ok=True)

        # Create information file
        infofile = open("output/" + date + "/" + filename + "/information.txt", "w")
        try:
            infofile.write(((str(info[i][0]) + ", " + str(info[i][1])).replace("Organization Name ", "") + "\n\n" + str(info[i][2]) + "\n\n" +
                        str(info[i][3]) + "\n\n" + str(info[i][4]) + "\n\n" + str(info[i][5]) + "\n\n" + info[i][6] + "\n\n" + str(info[i][7]) +
                        "\n\n" + info[i][8] + "\n\n" + info[i][9]).replace("\u2212", "-"))
        except:
            infofile.write("Error in encoding character from coop: " + info[i][0] + ", " + info[i][1])
            infofile.write("Please report - https://forms.gle/p8X8zCwHLGct85fY8")

        infofile.close()

        # Create cover letter file
        coverletterfile = open("output/" + date + "/" + filename +"/Cover Letter.txt", "w")
        coverletter = CoverLetter(info[i][8], info[i][9], info[i][0], info[i][1])
        coverletterfile.write(coverletter)
        coverletterfile.close()

        # Create pdf
        pdf = fpdf.fpdf.FPDF()
        pdf.add_font("ARIAL", "", "ARIAL.ttf", uni=True)
        pdf.add_page()
        pdf.set_font("ARIAL", size=11)

        coverletter = coverletter.format(info[i][0], info[i][1], "\n", date).replace("â€™", "'")
        coverletter = coverletter.split("\n")

        for para in coverletter:
            pdf.multi_cell(w=195, h=5, txt=para, align='L')
        pdf.output("output/" + date + "/" + filename + "/Cover Letter.pdf")
        pdf.close()

        # Switch back to window with list of postings
        driver.close()
        driver.switch_to.window(driver.window_handles[0])
        time.sleep(0.1)
        print(f"{GREEN}" + str(i+1) + "/" + str(len(links)) + f"{RESET}")
    driver.quit()


def CoverLetter(jobdesc, qualifications, jobtitle, organizationname):
    # Open paragraphs and keywords
    keywordfile = open("coverletterinfo/keywords.txt", "r")
    paragraphfile = open("coverletterinfo/paragraphs.txt", "r")

    # Read the opening and closing paragraph
    openparagraph = paragraphfile.readline().strip()
    closeparagraph = paragraphfile.readline().strip()

    # Reads keywords and paragraphs linked to them
    keyworddict = {}
    for kline in keywordfile:
        pline = paragraphfile.readline().strip()
        for word in kline.strip().split(";"):
            keyworddict[word] = pline

    # Closes files
    keywordfile.close()
    paragraphfile.close()

    # Adds opening paragraph to cover letter
    coverletter = ""
    coverletter += (openparagraph + "\n\n")

    # Checks if keyword is in qualifications or job information, and if so, adds them to the cover letter. Also prevents duplicates
    for keyword in keyworddict.keys():
        if keyword.lower() in (jobdesc + qualifications).lower() and keyworddict[keyword] not in coverletter:
            coverletter += (keyworddict[keyword] + "\n\n")

    # Adds closing paragraph, then replaces {0} with job title, {1} with organization name, {2} with returns, and {3} with today's date
    coverletter += closeparagraph
    coverletter = coverletter.format(jobtitle, organizationname, "\n", date)

    return coverletter


if __name__ == "__main__":
    Setup()
    Scraper()
    print(f"{GREEN}All done!\n{RESET}")
    time.sleep(3)
