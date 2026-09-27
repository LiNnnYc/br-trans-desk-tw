// 憑證欄位譯名對照（/glossary/cert-fields/）的唯一資料來源。
//
// 中文欄位名不是自己翻的，是從 Windows 的 MUI 資源與 Chrome 的 pak 檔實際抽出來的，
// 兩邊都會隨版本改字。重抽與比對一律用：
//
//     python scripts/extract_viewer_strings.py            # 憑證檢視器相關的 ID 區段
//     python scripts/extract_viewer_strings.py --grep 憑證  # 找某個詞現在怎麼顯示
//
// 改完 captureInfo 的版本與日期要一起更新。腳本抽不到的東西（Windows 的分頁名、
// 「顯示(S):」標籤寫在對話框樣板）若有收錄，是人工照畫面填的（例如「憑證路徑」），
// --verify 會報「部分相符」或「找不到」，屬正常。
// RFC 5280 欄位／ASN.1／OID 取自 web-spec-doc/X509憑證_欄位可用模組.txt（Appendix A 全文）。
// 整理過程與落差說明見 web-spec-doc/翻譯工作區/RFC5280_憑證檢視器欄位對照表.md。
//
// zh（本站譯名）：憑證本體與擴充欄位沿用《基本要求》第七章既有譯名。
// DN 屬性的中文名只用於本表（術語表），《基本要求》譯文仍保留英文識別碼，
// 不要回頭把第七章改成中文。keyUsage 位元、CRLReason 值不設中文名（showZh: false）。
// 留空＝本站沒有譯名，頁面顯示「—」。

export interface FieldRow {
  /** RFC 5280 的欄位／值識別碼，或表 8 的介面概念 */
  key: string;
  oid?: string;
  /** 本站譯名；本站沒有譯名者留空（DN 屬性的中文名只用於本表，見檔頭說明） */
  zh?: string;
  /** Windows 憑證檢視器實際顯示的中文；未在地化者留空 */
  winZh?: string;
  /** Windows 的英文原字；有 winZh 就一律填（即使與 key 相同也填） */
  winEn?: string;
  /** Windows 未提供在地化名稱時，畫面上實際顯示的字（英文或 OID） */
  winRaw?: string;
  chromeZh?: string;
  /** Chrome 的英文原字；有 chromeZh 就一律填（即使與 key 相同也填） */
  chromeEn?: string;
  chromeRaw?: string;
  note?: string;
}

export interface FieldTable {
  id: string;
  title: string;
  /** 索引列用的短標籤；未填則由 title 推導 */
  navLabel?: string;
  /** 標題右側的出處（RFC 節號等） */
  ref?: string;
  intro?: string;
  /** 第一欄的表頭文字 */
  keyHeader: string;
  /** 是否顯示「本站譯名」欄 */
  showZh: boolean;
  /** key 欄是否以等寬字顯示 */
  mono: boolean;
  rows: FieldRow[];
}

export const captureInfo = {
  date: '2026-09-22',
  chromeVersion: '153.0.8010.50',
  windows: 'Windows 10 22H2（zh-TW 語言套件）',
} as const;

export const certFieldTables: FieldTable[] = [
  {
    id: 'certificate',
    title: '憑證本體欄位',
    ref: '引用 RFC 5280 §4.1',
    keyHeader: 'RFC 5280 欄位',
    showZh: true,
    mono: true,
    rows: [
      {
        key: 'version',
        zh: '版本號',
        winZh: '版本號',
        winEn: 'Version',
        chromeZh: '版本',
        chromeEn: 'Version',
        note: '《基本要求》§7.1.1 要求為 v3；Chrome 的值顯示為「第 3 版」。',
      },
      {
        key: 'serialNumber',
        zh: '憑證序號',
        winZh: '序號',
        winEn: 'Serial number',
        chromeZh: '序號',
        chromeEn: 'Serial Number',
        note: '《基本要求》§7.1 要求至少 64 bit 亂度（資訊熵）。',
      },
      {
        key: 'signature',
        zh: '簽章演算法（內層）',
        winZh: '簽章演算法／簽章雜湊演算法',
        winEn: 'Signature algorithm／Signature hash algorithm',
        chromeZh: '憑證簽章演算法',
        chromeEn: 'Certificate Signature Algorithm',
        note: '兩個檢視器都無標示這個簽章演算法是 TBSCertificate 內層的 Signature 還是外層的 signatureAlgorithm；Windows 另把雜湊演算法獨立出一個欄位。',
      },
      {
        key: 'issuer',
        zh: '簽發者',
        winZh: '簽發者',
        winEn: 'Issuer／Issued by',
        chromeZh: '發行者',
        chromeEn: 'Issuer／Issued By',
      },
      {
        key: 'validity.notBefore',
        zh: '有效期自',
        winZh: '有效期自',
        winEn: 'Valid from',
        chromeZh: '此日期之後：（一般分頁作「發行日期」）',
        chromeEn: 'Not Before／Issued On',
        note: 'Chrome 的「此日期之後／此日期之前」翻譯與英文原文語意相反，原文語意為「不早於／不晚於」。',
      },
      {
        key: 'validity.notAfter',
        zh: '有效期到',
        winZh: '有效期到',
        winEn: 'Valid to',
        chromeZh: '此日期之前：（一般分頁作「到期日」）',
        chromeEn: 'Not After／Expires On',
      },
      {
        key: 'subject',
        zh: '主體名稱',
        winZh: '主體（一般分頁作「發給:」）',
        winEn: 'Subject／Issued to',
        chromeZh: '主體（一般分頁作「核發對象」）',
        chromeEn: 'Subject／Issued To',
      },
      {
        key: 'subjectPublicKeyInfo',
        zh: '主體公開金鑰資訊',
        winZh: '公開金鑰／公開金鑰參數',
        winEn: 'Public key／Public key parameters',
        chromeZh: '主體公開金鑰資訊',
        chromeEn: 'Subject Public Key Info',
        note: 'Chrome 於這個欄位下還會再區分「主體公開金鑰演算法」與「主體的公開金鑰」兩個子項目。',
      },
      {
        key: 'issuerUniqueID／subjectUniqueID',
        zh: '簽發者／主體唯一識別碼',
        note: 'RFC 5280 不建議使用，實務上不會出現，兩個檢視器都沒有對應名稱。',
      },
      {
        key: 'extensions',
        zh: '擴充欄位',
        winZh: '延伸',
        winEn: 'Extensions',
        chromeZh: '擴充功能',
        chromeEn: 'Extensions',
        note: 'Chrome 的「擴充功能」譯名與外掛功能 Chrome Extensions 同名，容易誤會。',
      },
      {
        key: 'tbsCertificate',
        note: 'tbsCertificate（To Be Signed Certificate）為 X.509 憑證中被簽章的主要資料結構。依據 RFC 5280 規範，CA 會對 tbsCertificate 的 DER 編碼值進行數位簽章，並將簽章演算法及簽章值分別記錄於憑證的 signatureAlgorithm 與 signatureValue 欄位，以供憑證完整性檢查及簽章驗證之用。',
      },
      {
        key: 'signatureAlgorithm',
        zh: '簽章演算法（外層）',
        note: '兩個檢視器的演算法欄位都不區分該欄位在 TBSCertificate 內層或外層；此值必須與內層 signature 欄位值完全相同。',
      },
      {
        key: 'signatureValue',
        zh: '簽章值',
        chromeZh: '憑證簽署值',
        chromeEn: 'Certificate Signature Value',
        note: 'Windows 憑證檢視器未列出此欄位。',
      },
      {
        key: 'Thumbprint（非 X.509 憑證欄位）',
        winZh: '憑證指紋／憑證指紋演算法',
        winEn: 'Thumbprint／Thumbprint algorithm',
        chromeZh: 'SHA-256 指紋',
        chromeEn: 'SHA-256 Fingerprints',
        note: '檢視器自己算出來的值，RFC 5280 規範未包含此欄位。若有人說「指紋不一樣」時，多半是計算演算法的不同。',
      },
    ],
  },
  {
    id: 'extensions-br',
    title: '擴充欄位：《基本要求》有規定的擴充欄位',
    navLabel: '擴充欄位（BR 有規定）',
    ref: '引用 RFC 5280 §4.2',
    keyHeader: 'RFC 5280 擴充欄位',
    showZh: true,
    mono: true,
    rows: [
      {
        key: 'authorityKeyIdentifier',
        oid: '2.5.29.35',
        zh: '授權單位金鑰識別碼',
        winZh: '授權單位金鑰識別元',
        winEn: 'Authority Key Identifier',
        chromeZh: '憑證授權單位金鑰識別碼',
        chromeEn: 'Certification Authority Key ID',
        note: 'Windows 於此欄位的 Identifier 翻譯採用「識別元」、同一個分頁裡的主體金鑰 Identifier 翻譯則採用「識別碼」。',
      },
      {
        key: 'subjectKeyIdentifier',
        oid: '2.5.29.14',
        zh: '主體金鑰識別碼',
        winZh: '主體金鑰識別碼',
        winEn: 'Subject Key Identifier',
        chromeZh: '憑證主體金鑰識別碼',
        chromeEn: 'Certificate Subject Key ID',
      },
      {
        key: 'keyUsage',
        oid: '2.5.29.15',
        zh: '憑證金鑰用途',
        winZh: '金鑰使用方法',
        winEn: 'Key Usage',
        chromeZh: '憑證金鑰用途',
        chromeEn: 'Certificate Key Usage',
      },
      {
        key: 'certificatePolicies',
        oid: '2.5.29.32',
        zh: '憑證原則',
        winZh: '憑證原則',
        winEn: 'Certificate Policies',
        chromeZh: '憑證原則',
        chromeEn: 'Certificate Policies',
        note:'依《基本要求》內容而言，應該要翻成「憑證政策」，但兩大軟體的憑證檢視器都譯為「憑證原則」，所以本站也跟著譯為「憑證原則」',
      },
      {
        key: 'subjectAltName',
        oid: '2.5.29.17',
        zh: '主體別名',
        winZh: '主體別名',
        winEn: 'Subject Alternative Name',
        chromeZh: '憑證主體替代名稱',
        chromeEn: 'Certificate Subject Alternative Name',
      },
      {
        key: 'basicConstraints',
        oid: '2.5.29.19',
        zh: '基本限制',
        winZh: '基本限制',
        winEn: 'Basic Constraints',
        chromeZh: '憑證基本限制',
        chromeEn: 'Certificate Basic Constraints',
        note: '兩邊於「值」的表現上差很多，見「檢視器介面用語」表的「basicConstraints 的內容值」列。',
      },
      {
        key: 'nameConstraints',
        oid: '2.5.29.30',
        zh: '名稱限制',
        winZh: '名稱限制',
        winEn: 'Name Constraints',
        chromeZh: '憑證名稱限制',
        chromeEn: 'Certificate Name Constraints',
      },
      {
        key: 'extKeyUsage',
        oid: '2.5.29.37',
        zh: '擴充金鑰使用方法',
        winZh: '增強金鑰使用方法',
        winEn: 'Enhanced Key Usage',
        chromeZh: '擴充金鑰使用方法',
        chromeEn: 'Extended Key Usage',
        note: 'Windows 詳細資料另有一欄位「增強金鑰使用方法 (內容)」，那是本機存放區的設定、不是憑證裡的欄位。',
      },
      {
        key: 'cRLDistributionPoints',
        oid: '2.5.29.31',
        zh: 'CRL 發布點',
        winZh: 'CRL 發佈點',
        winEn: 'CRL Distribution Points',
        chromeZh: 'CRL 發布點',
        chromeEn: 'CRL Distribution Points',
        note: 'Windows 用「發佈」，本站與 Chrome 用「發布」。',
      },
      {
        key: 'authorityInformationAccess',
        oid: '1.3.6.1.5.5.7.1.1',
        zh: '憑證機構資訊存取',
        winZh: '授權資訊存取',
        winEn: 'Authority Information Access',
        chromeZh: '授權單位資訊存取',
        chromeEn: 'Authority Information Access',
      },
      {
        key: 'signedCertificateTimestampList',
        oid: '1.3.6.1.4.1.11129.2.4.2',
        zh: '已簽章憑證時間戳記（SCT）清單',
        winZh: 'SCT 清單',
        winEn: 'SCT List',
        chromeZh: '憑證簽署的時間戳記清單',
        chromeEn: 'Signed Certificate Timestamp List',
        note: '非 RFC 5280 擴充欄位，此欄位定義於 RFC 6962 §3.3。',
      },
      {
        key: 'Precertificate Poison',
        oid: '1.3.6.1.4.1.11129.2.4.3',
        zh: '預簽憑證 Poison',
        winRaw: '直接顯示 OID',
        chromeRaw: '直接顯示 OID',
        note: '非 RFC 5280 擴充欄位，此欄位定義於 RFC 6962 §3.1，兩個檢視器都沒有在地化名稱。',
      },
      {
        key: 'id-pkix-ocsp-nocheck',
        oid: '1.3.6.1.5.5.7.48.1.5',
        winZh: 'OCSP 無撤銷檢查',
        winEn: 'OCSP No Revocation Checking',
        chromeRaw: '直接顯示 OID',
        note: '非 RFC 5280 擴充欄位，此欄位定義於 RFC 6960 §4.2.2.2.1。',
      },
    ],
  },
  {
    id: 'extensions-other',
    title: '擴充欄位：RFC 5280 有列出、《基本要求》未規定的擴充欄位',
    navLabel: '擴充欄位（BR 未規定）',
    ref: '引用 RFC 5280 §4.2',
    keyHeader: 'RFC 5280 擴充欄位',
    showZh: true,
    mono: true,
    rows: [
      {
        key: 'policyMappings',
        oid: '2.5.29.33',
        zh: '政策對應',
        winZh: '原則對應',
        winEn: 'Policy Mappings',
        chromeZh: '憑證政策對應關聯',
        chromeEn: 'Certificate Policy Mappings',
        note: 'Windows 用「原則」，本站與 Chrome 用「政策」。',
      },
      {
        key: 'issuerAltName',
        oid: '2.5.29.18',
        winZh: '簽發者別名',
        winEn: 'Issuer Alternative Name',
        chromeZh: '憑證發行者替代名稱',
        chromeEn: 'Certificate Issuer Alternative Name',
      },
      {
        key: 'subjectDirectoryAttributes',
        oid: '2.5.29.9',
        zh: '主體目錄屬性',
        winZh: '主體目錄屬性',
        winEn: 'Subject Directory Attributes',
        chromeZh: '憑證主體目錄屬性',
        chromeEn: 'Certificate Subject Directory Attributes',
      },
      {
        key: 'policyConstraints',
        oid: '2.5.29.36',
        zh: '政策限制',
        winZh: '原則限制',
        winEn: 'Policy Constraints',
        chromeZh: '憑證原則限制',
        chromeEn: 'Certificate Policy Constraints',
      },
      {
        key: 'inhibitAnyPolicy',
        oid: '2.5.29.54',
        zh: '禁止 anyPolicy',
        winZh: '禁止任何原則',
        winEn: 'Inhibit Any Policy',
        chromeRaw: '直接顯示 OID',
      },
      {
        key: 'freshestCRL',
        oid: '2.5.29.46',
        winZh: '最新的 CRL',
        winEn: 'Freshest CRL',
        chromeRaw: '直接顯示 OID',
      },
      {
        key: 'subjectInfoAccess',
        oid: '1.3.6.1.5.5.7.1.11',
        winZh: '主體資訊存取',
        winEn: 'Subject Information Access',
        chromeRaw: '直接顯示 OID',
      },
      {
        key: 'privateKeyUsagePeriod',
        oid: '2.5.29.16',
        winZh: '私密金鑰使用期限',
        winEn: 'Private Key Usage Period',
        chromeRaw: '直接顯示 OID',
      },
    ],
  },
  {
    id: 'key-usage',
    title: 'keyUsage 位元值',
    ref: '引用 RFC 5280 §4.2.1.3',
    intro:
      'keyUsage（憑證金鑰用途）為 X.509 憑證的擴充欄位，用於指出憑證所含公開金鑰的用途屬性。本站翻譯保留英文原文，不另行翻譯。Windows 於 zh-TW 介面下，亦將這九個位元值全部顯示為英文原文。',
    keyHeader: 'RFC 5280 位元',
    showZh: false,
    mono: true,
    rows: [
      { key: 'digitalSignature', winRaw: 'Digital Signature', chromeZh: '簽署', chromeEn: 'Signing' },
      { key: 'nonRepudiation', winRaw: 'Non-Repudiation', chromeZh: '不可否認性', chromeEn: 'Non-repudiation' },
      { key: 'keyEncipherment', winRaw: 'Key Encipherment', chromeZh: '金鑰編密', chromeEn: 'Key Encipherment' },
      { key: 'dataEncipherment', winRaw: 'Data Encipherment', chromeZh: '資料編密', chromeEn: 'Data Encipherment' },
      { key: 'keyAgreement', winRaw: 'Key Agreement', chromeZh: '金鑰協議', chromeEn: 'Key Agreement' },
      { key: 'keyCertSign', winRaw: 'Certificate Signing', chromeZh: '憑證簽署者', chromeEn: 'Certificate Signer' },
      {
        key: 'cRLSign',
        winRaw: 'CRL Signing／Off-line CRL Signing',
        chromeZh: 'CRL 簽署者',
        chromeEn: 'CRL Signer',
      },
      { key: 'encipherOnly', winRaw: 'Encipher Only', chromeZh: '只有 Encipher', chromeEn: 'Encipher Only' },
      { key: 'decipherOnly', winRaw: 'Decipher Only', chromeZh: '只有 Decipher', chromeEn: 'Decipher Only' },
    ],
  },
  {
    id: 'eku',
    title: 'extKeyUsage 值',
    ref: '引用 RFC 5280 §4.2.1.12',
    intro:
      'extKeyUsage（Extended Key Usage，擴充金鑰使用方法）為 X.509 憑證的擴充欄位，用於指出憑證中公開金鑰可使用的一項或多項特定用途目的，可作為憑證金鑰用途（Key Usage）所示基本用途的補充或替代。',
    keyHeader: 'RFC 5280 KeyPurposeId',
    showZh: false,
    mono: true,
    rows: [
      {
        key: 'id-kp-serverAuth',
        winZh: '伺服器驗證',
        winEn: 'Server Authentication',
        chromeZh: 'TLS WWW 伺服器驗證',
        chromeEn: 'TLS WWW Server Authentication',
      },
      {
        key: 'id-kp-clientAuth',
        winZh: '用戶端驗證',
        winEn: 'Client Authentication',
        chromeZh: 'TLS WWW 用戶端驗證',
        chromeEn: 'TLS WWW Client Authentication',
      },
      { key: 'id-kp-codeSigning', winZh: '程式碼簽署', winEn: 'Code Signing', chromeZh: '程式碼簽署', chromeEn: 'Code Signing' },
      {
        key: 'id-kp-emailProtection',
        winZh: '安全電子郵件',
        winEn: 'Secure Email',
        chromeZh: '電子郵件保護',
        chromeEn: 'Email Protection',
      },
      { key: 'id-kp-timeStamping', winZh: '時間戳記', winEn: 'Time Stamping', chromeZh: '時間戳記', chromeEn: 'Time Stamping' },
      {
        key: 'id-kp-OCSPSigning',
        winZh: 'OCSP 簽署',
        winEn: 'OCSP Signing',
        chromeZh: '簽署 OCSP 回應',
        chromeEn: 'Signing OCSP Responses',
      },
      { key: 'anyExtendedKeyUsage', winZh: '任何目的', winEn: 'Any Purpose', chromeZh: '不限', chromeEn: 'Any' },
    ],
  },
  {
    id: 'dn',
    title: 'DN 屬性（issuer／subject 裡面的子項目）',
    ref: '引用 RFC 5280 §4.1.2.4、§4.1.2.6',
    intro:
      'DN 為 Distinguished Name 的縮寫，本站翻譯為「唯一識別名稱」，是一種可具有多個子項目的結構容器，用來表示主體（Subject）和簽發者（Issuer）資訊。Chrome 的詳細資訊分頁完全不翻譯 DN 屬性，只顯示縮寫代碼；只有一般分頁把 CN／O／OU 三個完整名稱翻譯出來。',
    keyHeader: '屬性',
    showZh: true,
    mono: true,
    rows: [
      {
        key: 'commonName（CN）',
        oid: '2.5.4.3',
        zh: '一般名稱',
        winZh: '一般名稱',
        winEn: 'Common Name',
        chromeZh: '一般名稱 (CN)（顯示於「一般」分頁）',
        chromeEn: 'Common Name (CN)',
        chromeRaw: '「詳細資訊」分頁作 CN',
      },
      {
        key: 'organizationName（O）',
        oid: '2.5.4.10',
        zh: '組織名稱',
        winZh: '組織',
        winEn: 'Organization',
        chromeZh: '組織 (O)（顯示於「一般」分頁）',
        chromeEn: 'Organization (O)',
        chromeRaw: '「詳細資訊」分頁作 O',
      },
      {
        key: 'organizationalUnitName（OU）',
        oid: '2.5.4.11',
        zh: '組織單位名稱',
        winZh: '組織單位',
        winEn: 'Organizational Unit',
        chromeZh: '組織單位 (OU)（顯示於「一般」分頁）',
        chromeEn: 'Organizational Unit (OU)',
        chromeRaw: '「詳細資訊」分頁作 OU',
      },
      {
        key: 'localityName（L）',
        oid: '2.5.4.7',
        zh: '城市／鄉鎮名稱',
        winZh: '位置',
        winEn: 'Locality',
        chromeRaw: 'L',
      },
      {
        key: 'stateOrProvinceName（ST）',
        oid: '2.5.4.8',
        zh: '省份／州',
        winZh: '省',
        winEn: 'State Or Province',
        chromeRaw: 'ST',
        note: 'Windows 譯作「省」，台灣的憑證在這個欄位通常輸入「Taiwan」。',
      },
      {
        key: 'countryName（C）',
        oid: '2.5.4.6',
        zh: '國家代碼',
        winZh: '國家 (地區)',
        winEn: 'Country/Region',
        chromeRaw: 'C',
      },
      {
        key: 'serialNumber',
        oid: '2.5.4.5',
        zh: '註冊／登記號碼',
        winZh: '序號',
        winEn: 'Serial Number',
        chromeRaw: 'serialNumber',
        note: '與憑證本體欄位的 serialNumber（憑證序號）不是同一個東西。依據憑證種類，此欄可能會填列商業統一編號（EV 憑證）或身分證號碼（S/MIME 憑證）。',
      },
      { key: 'streetAddress', oid: '2.5.4.9', zh:'街道地址', winZh: '街道地址', winEn: 'Street Address', chromeRaw: 'STREET' },
      { key: 'postalCode', oid: '2.5.4.17', zh:'郵遞區號', chromeRaw: 'postalCode' },
      { key: 'businessCategory', oid: '2.5.4.15', zh:'組織形態', chromeRaw: 'businessCategory' },
      {
        key: 'domainComponent（DC）',
        oid: '0.9.2342.19200300.100.1.25',
        winZh: '網域元件',
        winEn: 'Domain Component',
        chromeRaw: 'DC',
      },
      {
        key: 'emailAddress',
        oid: '1.2.840.113549.1.9.1',
        zh: '電子郵件地址',
        winZh: '電子郵件地址',
        winEn: 'Email Address',
        chromeRaw: 'emailAddress／MAIL',
      },
      {
        key: 'jurisdictionLocalityName',
        oid: '1.3.6.1.4.1.311.60.2.1.1',
        zh: '設立／登記所在地城市／鄉鎮',
        chromeRaw: 'jurisdictionLocalityName',
      },
      {
        key: 'jurisdictionStateOrProvinceName',
        oid: '1.3.6.1.4.1.311.60.2.1.2',
        zh: '設立／登記所在地省份／州',
        chromeRaw: 'jurisdictionStateOrProvinceName',
      },
      {
        key: 'jurisdictionCountryName',
        oid: '1.3.6.1.4.1.311.60.2.1.3',
        zh: '設立／登記所在地國家代碼',
        chromeRaw: 'jurisdictionCountryName',
      },
      {
        key: 'organizationIdentifier',
        oid: '2.5.4.97',
        zh: '組織識別碼',
        note: '《基本要求》§7.1.4.2 只規定此屬性的編碼方式、未規定內容；EV 憑證須依《EV 指引》使用認可的註冊方案及規定的填列格式，目前有 NTR（各國商業統一編號）、VAT（各國商業稅務號碼）、PSD（歐盟 PSD 號碼）三種方案可選。',
      },
    ],
  },
  {
    id: 'general-name',
    title: 'GeneralName 型別（SAN／IAN／AIA 裡面的子項目）',
    ref: '引用 RFC 5280 §4.2.1.6',
    intro: 'GeneralName 型別是 ASN.1 語法的型別之一，也是設計 X.509 憑證的常見型別。Windows 對 GeneralName 型別完全不翻譯，畫面顯示為英文加等號的格式。',
    keyHeader: 'RFC 5280 型別',
    showZh: false,
    mono: true,
    rows: [
      { key: 'dNSName', winRaw: 'DNS Name=', chromeZh: 'DNS 名稱', chromeEn: 'DNS Name' },
      { key: 'iPAddress', winRaw: 'IP Address=', chromeZh: 'IP 位址', chromeEn: 'IP Address' },
      { key: 'uniformResourceIdentifier', winRaw: 'URL=', chromeRaw: 'URI' },
      { key: 'rfc822Name', winRaw: 'RFC822 Name=', chromeZh: '電子郵件地址', chromeEn: 'Email Address' },
      {
        key: 'directoryName',
        winRaw: 'Directory Address:',
        chromeZh: 'X.500 姓名',
        chromeEn: 'X.500 Name',
        note: 'Chrome 把 X.500 Name 的 Name 當成一種人名；其實這裡的 Name 也是個 ASN.1 型別。',
      },
      { key: 'x400Address', winRaw: 'X.400 Address=', chromeZh: 'X.400 地址', chromeEn: 'X.400 Address' },
      { key: 'ediPartyName', winRaw: 'EDI Party Name=', chromeZh: 'EDI 合作對象名稱', chromeEn: 'EDI Party Name' },
      { key: 'registeredID', winRaw: 'Registered ID=', chromeZh: '已註冊的 OID', chromeEn: 'Registered OID' },
      { key: 'otherName', winRaw: 'Other Name:' },
    ],
  },
  {
    id: 'crl',
    title: 'CRL（憑證廢止清冊）',
    ref: '引用 RFC 5280 §5',
    intro:
      '備註：本站依數發部用詞定義將 Revocation 譯為「廢止」，Windows 的翻譯為「撤銷」。當有人在憑證議題上講「撤銷」時，指的就是本站及數發部（含數發部管理下 CA）的「廢止」。Chrome 的憑證檢視器不顯示 CRL 內容。',
    keyHeader: 'RFC 5280',
    showZh: true,
    mono: true,
    rows: [
      {
        key: 'CertificateList',
        zh: '憑證廢止清冊（CRL）',
        winZh: '憑證撤銷清單',
        winEn: 'Certificate Revocation List',
      },
      { key: 'thisUpdate', zh: '本次更新時間', winZh: '有效日期', winEn: 'Effective date' },
      { key: 'nextUpdate', zh: '下次更新時間', winZh: '下次更新', winEn: 'Next update' },
      { key: 'revocationDate', zh: '廢止時間', winZh: '撤銷日期', winEn: 'Revocation date' },
      { key: 'cRLNumber', oid: '2.5.29.20', zh: 'CRL 序號', winZh: 'CRL 數目', winEn: 'CRL Number' },
      {
        key: 'issuingDistributionPoint',
        oid: '2.5.29.28',
        zh: '簽發發布點',
        winZh: '發行發佈點',
        winEn: 'Issuing Distribution Point',
      },
      {
        key: 'deltaCRLIndicator',
        oid: '2.5.29.27',
        winZh: 'Delta CRL 指示器',
        winEn: 'Delta CRL Indicator',
      },
      {
        key: 'cRLReasons',
        oid: '2.5.29.21',
        zh: 'CRL 廢止理由',
        winZh: 'CRL 理由代碼',
        winEn: 'CRL Reason Code',
      },
    ],
  },
  {
    id: 'crl-reason',
    title: 'CRLReason 列舉值',
    ref: '引用 RFC 5280 §5.3.1',
    intro: 'CRLReason 為 CRL 清單中每張憑證的廢止理由，有 10 個代碼可供選擇。本站翻譯保留英文原文識別碼，不另行翻譯。',
    keyHeader: 'RFC 5280 值',
    showZh: false,
    mono: true,
    rows: [
      {
        key: 'unspecified（0）',
        winZh: '未指定',
        winEn: 'Unspecified',
        chromeZh: '未使用',
        chromeEn: 'Unused',
        note: 'Chrome 於這個列舉值（代碼）的英文原文為 Unused，來自 RFC 5280 另一個型別 ReasonFlags 的第 0 個位元 unused；CRLReason 列舉值本身沒有 unused，值 7 則是保留不用。',
      },
      { key: 'keyCompromise（1）', winZh: '金鑰洩露', winEn: 'Key Compromise', chromeZh: '金鑰洩露', chromeEn: 'Key Compromise' },
      { key: 'cACompromise（2）', winZh: 'CA 洩露', winEn: 'CA Compromise', chromeZh: 'CA 洩露', chromeEn: 'CA Compromise' },
      { key: 'affiliationChanged（3）', winZh: '聯盟已變更', winEn: 'Affiliation Changed', chromeZh: '聯盟已變更', chromeEn: 'Affiliation Changed' },
      { key: 'superseded（4）', winZh: '已取代', winEn: 'Superseded', chromeZh: '已取代', chromeEn: 'Superseded' },
      { key: 'cessationOfOperation（5）', winZh: '操作停止', winEn: 'Cessation of Operation', chromeZh: '操作停止', chromeEn: 'Cessation of Operation' },
      { key: 'certificateHold（6）', winZh: '憑證保留', winEn: 'Certificate Hold', chromeZh: '憑證保留中', chromeEn: 'Certificate on Hold' },
      { key: 'removeFromCRL（8）', winZh: '從 CRL 移除', winEn: 'Remove from CRL' },
      { key: 'privilegeWithdrawn（9）', note: '兩個檢視器都沒有對應名稱。' },
      { key: 'aACompromise（10）', note: '兩個檢視器都沒有對應名稱。' },
    ],
  },
  {
    id: 'ui',
    title: '檢視器介面用語',
    intro: '從軟體安裝資料夾抽取 UI 文字的副產物，當作參考即可。',
    keyHeader: '概念',
    showZh: true,
    mono: false,
    rows: [
      {
        key: '欄位／值',
        winZh: '欄位／值',
        winEn: 'Field／Value',
        chromeZh: '憑證欄位／欄位值',
        chromeEn: 'Certificate Fields／Field Value',
      },
      {
        key: '憑證鏈',
        zh: '憑證鏈',
        winZh: '憑證路徑',
        winEn: 'Certification Path',
        chromeZh: '憑證階層',
        chromeEn: 'Certificate Hierarchy',
      },
      {
        key: 'critical',
        zh: '關鍵',
        winZh: '關鍵延伸',
        winEn: 'Critical Extensions',
        chromeZh: '重要／非重要',
        chromeEn: 'Critical／Not Critical',
      },
      {
        key: '檢視器標題',
        winZh: '憑證資訊',
        winEn: 'Certificate Information',
        chromeZh: '憑證檢視者',
        chromeEn: 'Certificate Viewer',
      },
      {
        key: 'basicConstraints 的內容值',
        zh: '顯示是否為 cA 和 pathLenConstraint 限制',
        winRaw: 'Subject Type=CA, Path Length Constraint=None',
        chromeZh: '這是憑證授權單位／中繼 CA 數目上限：無限制',
        chromeEn: 'Is a Certification Authority／Maximum number of intermediate CAs: unlimited',
      },
      {
        key: '憑證用途指示文字',
        winZh: '這個憑證的使用目的如下:',
        winEn: 'This certificate is intended for the following purpose(s):',
        chromeRaw: '無對應區塊',
      },
    ],
  },
];

export interface Gap {
  title: string;
  body: string;
}

/** 客服最容易被咬的落差，照嚴重程度排 */
export const certFieldGaps: Gap[] = [
  {
    title: 'critical：只有 Chrome 不稱作「關鍵」',
    body: '本站翻譯用「關鍵」，Windows 也用「關鍵延伸」，只有 Chrome 用「重要／非重要」。若指出「這個擴充欄位為關鍵」，則 Chrome 上找不到「關鍵」兩個字的擴充欄位。',
  },
  {
    title: 'Chrome 的「此日期之後／此日期之前」容易搞混',
    body: 'notBefore／notAfter 的語意是「不早於／不晚於」，Chrome 的翻譯與原文字義相反。Windows 的「有效期自／有效期到」則相對直覺；在討論有效期前，雙方應先確認是使用哪個憑證檢視器。',
  },
  {
    title: 'extensions 有各自不同的翻譯',
    body: '本站翻譯為「擴充欄位」、Windows「延伸」、Chrome「擴充功能」。Chrome 的翻譯跟瀏覽器外掛功能同名，會以為在講外掛（Plugins）。',
  },
  {
    title: 'Windows 的「增強金鑰使用方法 (內容)」不是 RFC 5280 憑證的擴充欄位',
    body: 'extKeyUsage 在 Windows 稱作「增強金鑰使用方法」（Enhanced Key Usage，微軟的舊稱），Chrome 與本站的翻譯為「擴充金鑰使用方法」。Windows certmgr.msc 於根憑證的詳細資料頁中，另有一項加上括號「(內容)」的同名項目；那是 Windows 憑證存放區的可編輯設定，用來限縮根憑證的金鑰用途，非 RFC 5280 規範的憑證內容。若發現有人的增強金鑰使用方法內容，跟您的 RFC 5280 知識不同，請先確認對方是在哪裡點開憑證檢視器。',
  },
  {
    title: 'Windows 不翻譯 keyUsage 位元值，卻翻譯 EKU 值',
    body: '同一個檢視器畫面裡，金鑰使用方法（keyUsage）的內容是英文（Digital Signature、Key Encipherment…），增強金鑰使用方法（extKeyUsage）的內容卻是中文（伺服器驗證、用戶端驗證）。Chrome 則是兩者都翻。導致同一張憑證在兩個檢視器下看起來像兩份文件。',
  },
  {
    title: 'Chrome 詳細資訊分頁不翻譯 DN 屬性',
    body: 'Chrome 詳細資訊分頁的欄位內容只顯示 CN／O／OU／L／ST／C 縮寫代碼，一般分頁才翻譯 CN／O／OU 的完整名稱。若有人說「上面只有英文縮寫」，可能是在看 Chrome 詳細資訊分頁。',
  },
  {
    title: '識別碼／識別元',
    body: 'Windows 憑證檢視器於同一個分頁裡的 AKI 是「授權單位金鑰識別元」、SKI 則是「主體金鑰識別碼」，其實兩者的 I 都是 Identifier。',
  },
  {
    title: '廢止／撤銷',
    body: '本站依數發部用詞定義將 Revocation 譯為「廢止」（憑證廢止清冊），Windows 的翻譯為「撤銷」、「撤銷清單」、「撤銷日期」。當有人在憑證議題上講「撤銷」時，指的就是本站及數發部（含數發部管理下 CA）的「廢止」。',
  },
  {
    title: 'Chrome 的「X.500 姓名」',
    body: '該欄應為 directoryName（X.500 Name），Chrome 把 Name 當成一種人名。其實這裡的 Name 也是個 ASN.1 型別。',
  },
  {
    title: 'Thumbprint／Fingerprint 指紋不是 X.509 憑證的規定內容',
    body: 'Windows 的「憑證指紋」與 Chrome 的「SHA-256 指紋」都是憑證檢視器當場算出來的。若有人說「指紋不一樣」時，多半是計算演算法的不同。',
  },
];
