
import puppeteer from 'puppeteer';
import {readFileSync,writeFileSync} from 'fs';
import readline from 'readline-sync';
import path from 'path';


function fileUrl(str) {
    if (typeof str !== 'string') {
        throw new Error('Expected a string');
    }

    var pathName = path.resolve(str).replace(/\\/g, '/');

    // Windows drive letter must be prefixed with a slash
    if (pathName[0] !== '/') {
        pathName = '/' + pathName;
    }

    return encodeURI('file://' + pathName);
};


let fsheetNum = process.argv[2];
console.log(fsheetNum)
let fsheetname = `fetchedsheet-${fsheetNum}.json` ;
let raw_sheet = readFileSync(`./toimg/${fsheetname}`).toString();
let sheet = JSON.parse(raw_sheet)
// console.log(sheet[2]);



async function elScreenShot(browser,page,el,i){
    let rimg = {question:null,explaination:null};
    let dimQn = await page.evaluate(`var a = $('.questionm'); [a[${i}].offsetLeft,a[${i}].offsetTop,a[${i}].offsetWidth,a[${i}].offsetHeight];`);
    let dimExp = await page.evaluate(`var a = $('.explaination'); [a[${i}].offsetLeft,a[${i}].offsetTop,a[${i}].offsetWidth,a[${i}].offsetHeight];`);
    
    // console.log({dimQn})
    let qnImg = await page.screenshot({
        clip:{
            x:dimQn[0],
            y:dimQn[1],
            width:dimQn[2],
            height:dimQn[3]
        }
    });
    rimg.question = qnImg;
    if(sheet[i].explanation_txt.trim() != ""){
        let expImg = await page.screenshot({
            clip:{
                x:dimExp[0],
                y:dimExp[1]+2,
                width:dimExp[2],
                height:dimExp[3]
            }
        });
        rimg.explaination = expImg;
    }
    return rimg;
    // const boundingBox = await el.boundingBox();
    // console.log(boundingBox)
}

async function screenShot(browser,page){
    // await page.screenshot({ path: 'tmp/example.png',fullPage:true });
    let el = await page.$$(`.question`);
    // console.log(el)
    let expList = [];
    let processedSheet = [];
    for(let i = 0; i<el.length;i++){
        if (i<95) continue;
        console.log(`${i} done`)
        let img = await elScreenShot(browser,page,el[i],i);
        expList.push(img);
        processedSheet[i] = {
            img: {
                question: img.question.toString('base64'),
                explaination: (img.explaination == null)?null:img.explaination.toString('base64')
            },
            ...sheet[i]
        }
        // if (i == 10) break;
        // break

    }
    // console.log(processedSheet[0]);
    console.log('FP screenshot done')
    return processedSheet;
}


;(async () => {
  const browser = await puppeteer.launch({headless:true,args: ['--no-sandbox']});
  const page = await browser.newPage();
  await page.goto(fileUrl('./toimg/template.html'),{
      waitUntil: 'networkidle0',
  });
  console.log('Page loaded')
  await page.evaluate(`fileLoaded("${Buffer.from(raw_sheet).toString('base64')}")`)
  await page.waitForSelector('#done-loading');
  console.log('Math rendered');
  await page.waitForTimeout(3000)
  console.log('XHR loaded');
  let processedSheet = await screenShot(browser,page);
  let fpw = path.join(path.resolve(),`./processedsheets/processed-${fsheetNum}.json`);
  console.log(fpw);
  writeFileSync(fpw,JSON.stringify(processedSheet))
  writeFileSync('tmp/example.png',Buffer.from(processedSheet[98]['img']['question'],'base64'))

  await browser.close();
})();