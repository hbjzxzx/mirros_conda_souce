from selenium import webdriver
from urllib.request import urlretrieve
from tqdm import tqdm
import os, time

class TqdmUpTo(tqdm):
    """Provides `update_to(n)` which uses `tqdm.update(delta_n)`."""
    def update_to(self, b=1, bsize=1, tsize=None):
        """
        b  : int, optional
            Number of blocks transferred so far [default: 1].
        bsize  : int, optional
            Size of each block (in tqdm units) [default: 1].
        tsize  : int, optional
            Total size (in tqdm units). If [default: None] remains unchanged.
        """
        if tsize is not None:
            self.total = tsize
        self.update(b * bsize - self.n)  # will also set self.n = b * bsize


def down_load_file(url, local_url, file_name):
    print('download {}'.format(file_name))
    with TqdmUpTo(unit='B', unit_scale=True, miniters=1,) as t:
        urlretrieve(url, local_url, t.update_to)

def parse_tr(tr):
    tds = tr.find_elements_by_tag_name('td')
    file_name = tds[0].find_element_by_tag_name('a').text
    size = tds[1].text
    file_time = tds[2].text
    return file_name, size, file_time

def mirror_this_page(remote_url, local_url='.'):
    option = webdriver.ChromeOptions()
    option.add_argument('headless')
    #br = webdriver.Chrome(options=option)
    br = webdriver.Chrome()
    br.get(remote_url)
    time.sleep(5)
    tbody = br.find_element_by_xpath('//*[@id="list"]/tbody')
    trs = tbody.find_elements_by_tag_name('tr')[1:]
    
    for tr in trs:
        file_name, size, file_time = parse_tr(tr)
        if size == '-':
            # this is an dir recurse function
            os.mkdir(os.path.join(local_url, file_name))
            mirror_this_page(remote_url + file_name, os.path.join(local_url, file_name) )
        else:
            # download file
            try:
                down_load_file(remote_url + file_name, os.path.join(local_url, file_name), file_name)
                with open(os.path.join(local_url, 'record.txt'), 'a') as record:
                    record.write("{}:{}\n".format(file_name, file_time))
            except Exception as e:
                with open('record_fail.txt', 'a') as record:
                    record.write("{}:{}, expect_local_path:{}\n".format(remote_url + file_name, str(e), os.path.join(local_url, file_name)))

if __name__ == "__main__":
    remote_root = 'https://mirrors.tuna.tsinghua.edu.cn/anaconda/'
    local_root = './mirrors'
    if os.path.isdir(local_root):
        mirror_this_page(remote_root, local_root)
    else:
        print('local_root not exist!!!')