# BR_archive — 上游英文原文的版本快照

本站每次升版前，會把**當時的** `upstream/BR.md` 複製一份到這裡，檔名帶版本號：

```
BR_archive/BR-v2.2.7.md    ← TLS BR v2.2.7 原文（2026-05-19）
BR_archive/BR-v2.3.0.md    ← TLS BR v2.3.0 原文（2026-09-07）
```

## 為什麼現行檔不帶版本號

`upstream/BR.md` 永遠是「目前對照用的上游原文」，檔名固定。`src/lib/version.ts`
只讀它，版本身分取自檔內 front-matter 的 `subtitle: Version X`。若現行檔也帶版本號，
就會出現兩個地方都自稱上游來源，遲早漂移。

**封存檔則相反**：程式從不讀取，純粹給人找檔案用，所以檔名帶版本號最實用。

## 與 git tag 的關係

舊版原文同時存在於 `br-v<版本>` tag（`git show br-v2.2.7:upstream/BR.md`）。
這裡的副本是為了**不必下 git 指令就能開啟比對**；`scripts/diff_br_versions.py`
兩種來源都吃，優先用這裡的檔案，找不到才回頭去 tag 取。

## 不放進 public/

這些是 CA/Browser Forum 的英文原文（CC BY 4.0，再散布是允許的），但鏡像英文原文
不是本站的任務（PRD 的定位是繁中翻譯），故只留在 repo 內、不隨網站發布。
