// ある時刻以降に更新のあったpdf情報を全取得して表示する
// 検証ツールの console にファイル全て貼り付けて実行する
// HOW TO USE:
//    getPdfSince(), getPdfSince("2021/07/03")
//
// CAUTION: 同日の取り扱いには注意
//
function getPdfSince(lastAddAt) {
  // dateに指定がない時は０を入れる。
  let date = (lastAddAt == undefined)? 0 : lastAddAt;
  const divs = document.getElementsByTagName("div");
  let base_url = "https://drive.google.com/file/d/";
  let suffix = "/view?usp=sharing";

  let pdfInfos = [];
  let info = {};
  for (let i = 0; i < divs.length; i++) {
    let div = divs[i];
    // 必要な情報を含んでいるであろう、divの親を取得
    if (div.hasAttribute("data-id")) {
      const inner_divs = div.getElementsByTagName("div");
      const inner_spans = div.getElementsByTagName("span");
      info = {};
      info["url"] = base_url + div.getAttribute("data-id") + suffix;
      // pdfの名前の取得
      for (let i = 0; i < inner_divs.length; i++) {
        const inner_div = inner_divs[i];
        if (isPdfName(inner_div.innerHTML)){
          info["name"] = inner_div.textContent;
          pdfInfos.push(info);
          break
        }
      }
      // 最終更新日時の取得
      for (let i = 0; i < inner_spans.length; i++) {
        const inner_span = inner_spans[i];
        const {hasUA, updated_at} = getUpdatedAt(inner_span);
        if (hasUA) {
          info["updated_at"] = updated_at;
          break
        }
      }
    }
  }
  printDataSince(pdfInfos, date);
}

function isPdfName(content) {
  return content.slice(-4) === ".pdf"
}

function getUpdatedAt(elm) {
  let has_updated_at = elm.hasAttribute("data-tooltip")
  && (elm.getAttribute("data-tooltip").slice(0,4) === "最終更新");
  let updated_at = "";
  if (has_updated_at) {
    let split_date = elm.getAttribute("data-tooltip").split(":");
    if (split_date.length === 2) {
      // "最終更新 : 07/03" みたいな場合
      updated_at = split_date[1].trim()
    } else {
      // "最終更新 : 20:03" みたいな場合
      updated_at = split_date.slice(1).join(":").trim();
    }
  }
  return {
    hasUA: has_updated_at,
    updated_at: updated_at
  }
}

// Notionに取り込みやすいように、綺麗なCSVで表示
// 区切り文字は変えられる
function printDataSince(pdfInfos, date) {
  console.log(pdfInfos);
  // CSV の区切り文字
  const SERPARATOR = "\t";
  let result = "";
  for (let i = 0; i < pdfInfos.length; i++) {
    const info = pdfInfos[i];
    if (isInfoNew(info.updated_at, date)) {
      // 必要な情報があれば追加する
      result += info.name + SERPARATOR + info.url + "\n";
    }
  }
  console.log(result);
}

function isInfoNew(pdfDate, date) {
  // pdfDateが時間（当日の更新）ならtrueにする
  if (pdfDate.includes(":")) {
    return true
  }
  // Unix時間で比較
  return (Date.parse(pdfDate) > Date.parse(date))
}
