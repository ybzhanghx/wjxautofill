from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support.expected_conditions import alert_is_present
from pyquery import PyQuery as pq
from lxml import etree
import release.readconfig as readconfig

browser = webdriver.Chrome()
wait = WebDriverWait(browser, 5)
config = readconfig.Config('my.ini')


def login():
    '''
    模拟登陆
    :return:
    //todo 需要增加识别验证码功能
    '''
    browser.get(config.loginurl)
    wait.until(
        EC.presence_of_element_located((By.ID, 'UserName'))
    ).send_keys(config.loginusername)

    wait.until(
        EC.presence_of_element_located((By.ID, 'Password'))
    ).send_keys(config.loginpassoword)

    wait.until(
        EC.element_to_be_clickable((By.ID, 'LoginButton'))
    ).click()


def get_questionnaire_list_in_page():
    '''
    遍历问卷列表，
    :return:
    '''
    browser.get(config.mutualurl)
    docs = etree.HTML(browser.page_source)

    savefile("questionlist", browser.page_source)
    lists = docs.xpath('//*[@id="ctl02_ContentPlaceHolder1_divJoinData"]//a/@href')[1:]
    # lists = docs('#ctl02_ContentPlaceHolder1_divJoinData a').items()
    map(lambda x: autofill_questionnaires_node(config.baseurl + x), lists)


def autofill_questionnaires_node(url: str) -> None:
    browser.get(url)
    docs = pq(browser.page_source)
    if is_has_fill():
        return

    questionlists = docs('#fieldset1')
    for i, question in enumerate(questionlists('.div_question').items()):
        if len(question('.jqRadio')) > 0:
            ids = 'q' + str(i + 1) + '_2'
            inputs = browser.find_element_by_id(ids)
            # // *[ @ id = "q1_2"]//*[@id="q1_2"]//*[@id="q1_1"]
            #  '''//*[@id=''' + ids + '''"]/../div[1]''')
            #  // *[ @ id = "divquestion2"] / ul / li[1] / a
            inputs = browser.find_element_by_xpath('''//*[@id="''' + ids + '''"]/../a''')
            inputs.click()  # divquestion1 > ul:nth-child(2) > li:nth-child(1) > a
        elif len(question('.jqCheckbox')) > 0:
            ids = 'q' + str(i + 1) + '_1'
            inputs = browser.find_element_by_xpath('''//*[@id="''' + ids + '''"]/../a''')
            inputs.click()  # divquestion1 > ul:nth-child(2) > li:nth-child(1) >
        elif len(question('.inputtext')) > 0:
            browser.find_element_by_id('q' + str(i + 1)).send_keys('I dont know anything')
        else:
            break
    # submit = browser.find_element_by_xpath("//*[@id=\"submit_button\"]")
    # submit.click()
    # fail_submit()

    return
    # elif len(question('.lisort')) > 0:
    #     sortlen=len(question('.lisort').items())
    #     for j in range(1,sortlen+1):
    #         browser.find_element_by_id('q' + i+'_'+j).click()
    # elif len(question('.rowth'))>0:
    #     rowlen=len(question('.rowth').items())
    #     for j in range(sortlen):
    #         browser.find_element_by_name('q' + i + '_' +j).click()
    # EC.element_to_be_clickable((By.CSS_SELECTOR. '//input[@value="cv1"]').click()  # click


def is_has_fill() -> bool:
    ###判断是否填写过
    try:
        input = wait.until(
            EC.presence_of_element_located((By.XPATH, '''// *[ @ id = "divNotRun"] / div / div / input''')))  # 等待弹出窗口出现
        input.click()
        return True
    except TimeoutException:
        return False


def fail_submit() -> None:
    try:
        wait.until(alert_is_present())  # 等待弹出窗口出现，
        browser.switch_to.alert.accept()
    except TimeoutException:
        return


def savefile(filename: str, file: str) -> None:
    filename = removechar(filename, '/')
    filename = removechar(filename, '?')
    filename = removechar(filename, '.')
    filename = removechar(filename, '%')
    with open(filename + '.html', 'w+', encoding='utf-8') as f:
        f.write(file)


def removechar(strs: str, flag: str) -> str:
    strarr = strs.split(flag)
    strs = ''.join(strarr)
    return strs


if __name__ == '__main__':
    login()
    # questionid=getquestionid(browser,wait)
    get_questionnaire_list_in_page()
    # html = browser.page_source
    # doc = pq(html)
    # print(doc)
