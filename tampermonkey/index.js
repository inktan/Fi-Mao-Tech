alert('hello world');
const title = document.title.replace('(豆瓣)', '').trim()
const doulist = document.querySelector('#subject-doulist')
const sourceBox = document.createElement('div')
doulist.insertAdjacentElement('beforebegin', sourceBox)

const buttons = [
    { name: '猫狸微搜', url: 'https://www.alipansou.com/search?k=' },
    { name: '4K彩视', url: 'https://www.4kvm.org/xssearch?s=' },
    { name: 'APP影视', url: 'https://www.appmovie.vip/index.php/vod/search.html?wd=' },
    { name: '毕方铺', url: 'https://www.iizhi.cn/resource/search/' }
]
let html = `<h2><i class="">外部资源</i></h2>`

const style = `background:#F0F3F5;border:none;padding:2px 6px;margin:2px;`


buttons.forEach(item => {
    html += `<button style="${style}" data-url="${item.url}">${item.name}<button>`
})

sourceBox.innerHTML = html;
sourceBox.style.marginBottom = '20px';

sourceBox.addEventListener('click', event => {
    const target = event.target
    if (target.tagName === 'BUTTON') {
        const url = target.getAttribute('data-url')
        window.open(url + title)
    }
})
