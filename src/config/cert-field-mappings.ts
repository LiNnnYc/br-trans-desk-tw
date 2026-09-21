// 憑證欄位譯名對照（/glossary/cert-fields/）的唯一資料來源。
//
// 中文欄位名不是自己翻的，是從 Windows 的 MUI 資源與 Chrome 的 pak 檔實際抽出來的，
// 兩邊都會隨版本改字。重抽與比對一律用：
//
//     python scripts/extract_viewer_strings.py            # 憑證檢視器相關的 ID 區段
//     python scripts/extract_viewer_strings.py --grep 憑證  # 找某個詞現在怎麼顯示
//
// 改完 captureInfo 的版本與日期要一起更新。腳本抽不到的東西（Windows 的分頁名、
// 「顯示(S):」標籤寫在對話框樣板）本表刻意未收。
// RFC 5280 欄位／ASN.1／OID 取自 web-spec-doc/X509憑證_欄位可用模組.txt（Appendix A 全文）。
// 整理過程與落差說明見 web-spec-doc/翻譯工作區/RFC5280_憑證檢視器欄位對照表.md。
//
// zh（本站譯名）沿用《基本要求》第七章既有譯名，未另創；第七章保留英文識別碼的項目
// （keyUsage 位元、DN 屬性、CRLReason 值）此處一律留空，不要補中文。

export interface FieldRow {
  /** RFC 5280 的欄位／值識別碼，或表 8 的介面概念 */
  key: string;
  oid?: string;
  /** 本站譯名；第七章保留原文識別碼者留空 */
  zh?: string;
  /** Windows 憑證檢視器實際顯示的中文；未在地化者留空 */
  winZh?: string;
  /** Windows 的英文原字，僅在與 key 不同時填 */
  winEn?: string;
  /** Windows 未提供在地化名稱時，畫面上實際顯示的字（英文或 OID） */
  winRaw?: string;
  chromeZh?: string;
  chromeEn?: string;
  chromeRaw?: string;
  note?: string;
  /** 三邊講法不一致、客服容易被咬的列 */
  warn?: boolean;
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
    ref: 'RFC 5280 §4.1',
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
        note: '《基本要求》§7.1.1 要求 v3；Chrome 的值顯示為「第 3 版」。',
      },
      {
        key: 'serialNumber',
        zh: '憑證序號',
        winZh: '序號',
        winEn: 'Serial number',
        chromeZh: '序號',
        chromeEn: 'Serial Number',
        note: '《基本要求》§7.1 要求至少 64 bit 亂度。',
      },
      {
        key: 'signature（內層）',
        zh: '簽章演算法（內層）',
        winZh: '簽章演算法／簽章雜湊演算法',
        winEn: 'Signature algorithm／Signature hash algorithm',
        chromeZh: '憑證簽章演算法',
        chromeEn: 'Certificate Signature Algorithm',
        note: '兩個檢視器都不標示這是內層或外層；Windows 另把雜湊演算法拆成一列。',
      },
      {
        key: 'issuer',
        zh: '簽發者名稱',
        winZh: '簽發者（一般分頁作「簽發者:」）',
        winEn: 'Issuer／Issued by',
        chromeZh: '發行者（一般分頁亦作「發行者」）',
        chromeEn: 'Issuer／Issued By',
      },
      {
        key: 'validity.notBefore',
        zh: '生效時間',
        winZh: '有效期自',
        winEn: 'Valid from',
        chromeZh: '此日期之後：（一般分頁作「發行日期」）',
        chromeEn: 'Not Before／Issued On',
        warn: true,
        note: 'Chrome 的「此日期之後／此日期之前」字面與直覺相反，語意是「不早於／不晚於」。',
      },
      {
        key: 'validity.notAfter',
        zh: '屆期時間',
        winZh: '有效期到',
        winEn: 'Valid to',
        chromeZh: '此日期之前：（一般分頁作「到期日」）',
        chromeEn: 'Not After／Expires On',
        warn: true,
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
        note: 'Chrome 下再分「主體公開金鑰演算法」與「主體的公開金鑰」兩層。',
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
        warn: true,
        note: 'Chrome 的「擴充功能」與瀏覽器外掛同名，客戶容易誤會。',
      },
      {
        key: 'signatureAlgorithm（外層）',
        zh: '簽章演算法（外層）',
        note: '兩個檢視器都不與內層分列；必須與內層完全相同。',
      },
      {
        key: 'signature（簽章值）',
        zh: '簽章值',
        chromeZh: '憑證簽署值',
        chromeEn: 'Certificate Signature Value',
        note: 'Windows 未單獨列出。',
      },
      {
        key: '（非憑證欄位）',
        winZh: '憑證指紋／憑證指紋演算法、易記名稱、描述',
        winEn: 'Thumbprint／Thumbprint algorithm',
        chromeZh: 'SHA-256 指紋（憑證／公開金鑰）',
        chromeEn: 'SHA-256 Fingerprints',
        note: '檢視器自己算出來的，不在憑證裡。客戶說「指紋跟你給的不一樣」多半是演算法不同。',
      },
    ],
  },
  {
    id: 'extensions-br',
    title: '擴充欄位：《基本要求》第七章有規定的',
    navLabel: '擴充欄位（有規定）',
    ref: 'RFC 5280 §4.2',
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
        warn: true,
        note: 'Windows 同一畫面裡這個用「識別元」、主體那個用「識別碼」。',
      },
      {
        key: 'subjectKeyIdentifier',
        oid: '2.5.29.14',
        zh: '主體金鑰識別碼',
        winZh: '主體金鑰識別碼',
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
        chromeZh: '憑證原則',
      },
      {
        key: 'subjectAltName',
        oid: '2.5.29.17',
        zh: '主體別名',
        winZh: '主體別名',
        chromeZh: '憑證主體替代名稱',
        chromeEn: 'Certificate Subject Alternative Name',
      },
      {
        key: 'basicConstraints',
        oid: '2.5.29.19',
        zh: '基本限制',
        winZh: '基本限制',
        chromeZh: '憑證基本限制',
        warn: true,
        note: '兩邊「值」的呈現差很多，見「檢視器介面用語」表最後一列。',
      },
      {
        key: 'nameConstraints',
        oid: '2.5.29.30',
        zh: '名稱限制',
        winZh: '名稱限制',
        chromeZh: '憑證名稱限制',
      },
      {
        key: 'extKeyUsage',
        oid: '2.5.29.37',
        zh: '擴充金鑰使用方法',
        winZh: '增強金鑰使用方法',
        winEn: 'Enhanced Key Usage',
        chromeZh: '擴充金鑰使用方法',
        chromeEn: 'Extended Key Usage',
        warn: true,
        note: 'Windows 詳細資料另有一列「增強金鑰使用方法 (內容)」，那是本機存放區的設定、不是憑證裡的欄位。',
      },
      {
        key: 'cRLDistributionPoints',
        oid: '2.5.29.31',
        zh: 'CRL 發布點',
        winZh: 'CRL 發佈點',
        chromeZh: 'CRL 發布點',
        warn: true,
        note: 'Windows 用「發佈」，本站與 Chrome 用「發布」。',
      },
      {
        key: 'authorityInformationAccess',
        oid: '1.3.6.1.5.5.7.1.1',
        zh: '憑證機構資訊存取',
        winZh: '授權資訊存取',
        winEn: 'Authority Information Access',
        chromeZh: '授權單位資訊存取',
      },
      {
        key: 'SCT 清單',
        oid: '1.3.6.1.4.1.11129.2.4.2',
        zh: '已簽章憑證時間戳記（SCT）清單',
        winZh: 'SCT 清單',
        winEn: 'SCT List',
        chromeZh: '憑證簽署的時間戳記清單',
        chromeEn: 'Signed Certificate Timestamp List',
        note: 'RFC 6962 §3.3，不在 RFC 5280。',
      },
      {
        key: '預簽憑證 Poison',
        oid: '1.3.6.1.4.1.11129.2.4.3',
        zh: '預簽憑證 Poison',
        winRaw: '顯示 OID',
        chromeRaw: '顯示 OID',
        note: 'RFC 6962 §3.1，兩個檢視器都沒有在地化名稱。',
      },
      {
        key: 'id-pkix-ocsp-nocheck',
        oid: '1.3.6.1.5.5.7.48.1.5',
        zh: 'id-pkix-ocsp-nocheck',
        winZh: 'OCSP 無撤銷檢查',
        winEn: 'OCSP No Revocation Checking',
        chromeRaw: '顯示 OID',
        note: 'RFC 6960 §4.2.2.2.1。',
      },
    ],
  },
  {
    id: 'extensions-other',
    title: '擴充欄位：RFC 5280 有、《基本要求》未使用的',
    navLabel: '擴充欄位（未使用）',
    ref: 'RFC 5280 §4.2',
    keyHeader: 'RFC 5280 擴充欄位',
    showZh: true,
    mono: true,
    rows: [
      {
        key: 'policyMappings',
        oid: '2.5.29.33',
        zh: '原則對應',
        winZh: '原則對應',
        chromeZh: '憑證政策對應關聯',
        warn: true,
        note: 'Chrome 用「政策」，本站與 Windows 用「原則」。',
      },
      {
        key: 'issuerAltName',
        oid: '2.5.29.18',
        zh: '簽發者別名',
        winZh: '簽發者別名',
        chromeZh: '憑證發行者替代名稱',
      },
      {
        key: 'subjectDirectoryAttributes',
        oid: '2.5.29.9',
        zh: '主體目錄屬性',
        winZh: '主體目錄屬性',
        chromeZh: '憑證主體目錄屬性',
      },
      {
        key: 'policyConstraints',
        oid: '2.5.29.36',
        zh: '原則限制',
        winZh: '原則限制',
        chromeZh: '憑證原則限制',
      },
      {
        key: 'inhibitAnyPolicy',
        oid: '2.5.29.54',
        zh: '禁止 anyPolicy',
        winZh: '禁止任何原則',
        winEn: 'Inhibit Any Policy',
        chromeRaw: '顯示 OID',
      },
      {
        key: 'freshestCRL',
        oid: '2.5.29.46',
        zh: '最新 CRL（delta CRL 指標）',
        winZh: '最新的 CRL',
        chromeRaw: '顯示 OID',
      },
      {
        key: 'subjectInfoAccess',
        oid: '1.3.6.1.5.5.7.1.11',
        zh: '主體資訊存取',
        winZh: '主體資訊存取',
        chromeRaw: '顯示 OID',
      },
      {
        key: 'privateKeyUsagePeriod',
        oid: '2.5.29.16',
        zh: '私密金鑰使用期間',
        winZh: '私密金鑰使用期限',
        chromeRaw: '顯示 OID',
      },
    ],
  },
  {
    id: 'key-usage',
    title: 'keyUsage 位元值',
    ref: 'RFC 5280 §4.2.1.3',
    intro:
      '本站第七章保留英文識別碼（寫成「digitalSignature 旗標位元」），不另造中文名。Windows 在 zh-TW 介面下這九個位元全部顯示英文——字串表的中英文完全相同，不是抽取失敗。',
    keyHeader: 'RFC 5280 位元',
    showZh: false,
    mono: true,
    rows: [
      { key: 'digitalSignature', winRaw: 'Digital Signature', chromeZh: '簽署', chromeEn: 'Signing', warn: true },
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
    ref: 'RFC 5280 §4.2.1.12',
    intro:
      'Windows 另有「所有應用程式原則」（All application policies）等 Microsoft 自家用途，不是 RFC 5280 的項目，別混為一談。',
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
      { key: 'id-kp-codeSigning', winZh: '程式碼簽署', winEn: 'Code Signing', chromeZh: '程式碼簽署' },
      {
        key: 'id-kp-emailProtection',
        winZh: '安全電子郵件',
        winEn: 'Secure Email',
        chromeZh: '電子郵件保護',
        chromeEn: 'Email Protection',
      },
      { key: 'id-kp-timeStamping', winZh: '時間戳記', winEn: 'Time Stamping', chromeZh: '時間戳記' },
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
    title: 'DN 屬性（issuer／subject 裡面的東西）',
    ref: 'RFC 5280 §4.1.2.4、§4.1.2.6',
    intro:
      'Chrome 的詳細資訊樹完全不翻譯 DN 屬性，只顯示短碼；只有一般分頁把 CN／O／OU 三個譯出來。客戶說「上面只有英文縮寫」，通常就是在看詳細資訊樹。',
    keyHeader: '屬性',
    showZh: true,
    mono: true,
    rows: [
      {
        key: 'commonName',
        oid: '2.5.4.3',
        zh: '保留原文識別碼',
        winZh: '一般名稱',
        winEn: 'Common Name',
        chromeZh: '一般分頁作「一般名稱 (CN)」',
        chromeRaw: '詳細資訊作 CN',
        warn: true,
      },
      {
        key: 'organizationName',
        oid: '2.5.4.10',
        zh: '保留原文識別碼',
        winZh: '組織',
        winEn: 'Organization',
        chromeZh: '一般分頁作「組織 (O)」',
        chromeRaw: '詳細資訊作 O',
      },
      {
        key: 'organizationalUnitName',
        oid: '2.5.4.11',
        zh: '保留原文識別碼',
        winZh: '組織單位',
        winEn: 'Organizational Unit',
        chromeZh: '一般分頁作「組織單位 (OU)」',
        chromeRaw: '詳細資訊作 OU',
      },
      {
        key: 'localityName',
        oid: '2.5.4.7',
        zh: '保留原文識別碼',
        winZh: '位置',
        winEn: 'Locality',
        chromeRaw: 'L',
      },
      {
        key: 'stateOrProvinceName',
        oid: '2.5.4.8',
        zh: '保留原文識別碼',
        winZh: '省',
        winEn: 'State Or Province',
        chromeRaw: 'ST',
        warn: true,
        note: 'Windows 譯作「省」，台灣憑證的這個欄位通常放縣市或「Taiwan」。',
      },
      {
        key: 'countryName',
        oid: '2.5.4.6',
        zh: '保留原文識別碼',
        winZh: '國家 (地區)',
        winEn: 'Country/Region',
        chromeRaw: 'C',
      },
      {
        key: 'serialNumber',
        oid: '2.5.4.5',
        zh: '保留原文識別碼',
        winZh: '序號',
        winEn: 'Serial Number',
        chromeRaw: 'serialNumber',
        note: '與憑證本體的 serialNumber 不是同一個東西。',
      },
      { key: 'streetAddress', oid: '2.5.4.9', winZh: '街道地址', winEn: 'Street Address', chromeRaw: 'STREET' },
      { key: 'postalCode', oid: '2.5.4.17', chromeRaw: 'postalCode' },
      { key: 'businessCategory', oid: '2.5.4.15', chromeRaw: 'businessCategory' },
      {
        key: 'domainComponent',
        oid: '0.9.2342.19200300.100.1.25',
        zh: '保留原文識別碼',
        winZh: '網域元件',
        winEn: 'Domain Component',
        chromeRaw: 'DC',
      },
      {
        key: 'emailAddress',
        oid: '1.2.840.113549.1.9.1',
        winZh: '電子郵件地址',
        winEn: 'Email Address',
        chromeRaw: 'emailAddress／MAIL',
      },
      {
        key: 'EV 管轄地三屬性',
        oid: '1.3.6.1.4.1.311.60.2.1.x',
        chromeRaw: 'jurisdictionLocalityName 等原文',
      },
    ],
  },
  {
    id: 'general-name',
    title: 'GeneralName 型別（SAN／IAN／AIA 裡面的東西）',
    ref: 'RFC 5280 §4.2.1.6',
    intro: 'Windows 這一組完全不翻譯，畫面上直接是英文加等號。',
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
        warn: true,
        note: 'Chrome 把 X.500 Name 的 Name 當成人名翻了。',
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
    ref: 'RFC 5280 §5',
    intro:
      '本站依中華電信 HiPKI CA CP/CPS 用「廢止」，Windows 用「撤銷」。客戶講「撤銷」時指的通常就是我們說的廢止。Chrome 的憑證檢視器不顯示 CRL 內容。',
    keyHeader: 'RFC 5280',
    showZh: true,
    mono: true,
    rows: [
      {
        key: 'CertificateList',
        zh: '憑證廢止清冊（CRL）',
        winZh: '憑證撤銷清單',
        winEn: 'Certificate Revocation List',
        warn: true,
      },
      { key: 'thisUpdate', zh: '本次更新時間', winZh: '有效日期', winEn: 'Effective date' },
      { key: 'nextUpdate', zh: '下次更新時間', winZh: '下次更新', winEn: 'Next update' },
      { key: 'revocationDate', zh: '廢止時間', winZh: '撤銷日期', winEn: 'Revocation date', warn: true },
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
        zh: 'delta CRL 指標',
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
    ref: 'RFC 5280 §5.3.1',
    intro: '本站第七章保留英文識別碼，不另造中文名。',
    keyHeader: 'RFC 5280 值',
    showZh: false,
    mono: true,
    rows: [
      {
        key: 'unspecified',
        winZh: '未指定',
        winEn: 'Unspecified',
        chromeZh: '未使用',
        chromeEn: 'Unused',
        warn: true,
        note: 'Chrome 那一列的英文是 Unused（ReasonFlags 的第 0 個位元），與 Windows 的 Unspecified 不是同一個來源字串。',
      },
      { key: 'keyCompromise', winZh: '金鑰洩露', chromeZh: '金鑰洩露' },
      { key: 'cACompromise', winZh: 'CA 洩露', chromeZh: 'CA 洩露' },
      { key: 'affiliationChanged', winZh: '聯盟已變更', chromeZh: '聯盟已變更' },
      { key: 'superseded', winZh: '已取代', chromeZh: '已取代' },
      { key: 'cessationOfOperation', winZh: '操作停止', chromeZh: '操作停止' },
      { key: 'certificateHold', winZh: '憑證保留', chromeZh: '憑證保留中' },
      { key: 'removeFromCRL', winZh: '從 CRL 移除' },
      { key: 'privilegeWithdrawn／aACompromise', note: '兩個檢視器都沒有對應名稱。' },
    ],
  },
  {
    id: 'ui',
    title: '檢視器介面用語',
    intro: 'Windows 的分頁名與「顯示」下拉標籤寫在對話框樣板、不在字串表，未收錄。',
    keyHeader: '概念',
    showZh: true,
    mono: false,
    rows: [
      {
        key: '欄位／值兩欄',
        winZh: '欄位／值',
        winEn: 'Field／Value',
        chromeZh: '憑證欄位／欄位值',
        chromeEn: 'Certificate Fields／Field Value',
      },
      {
        key: '憑證鏈',
        zh: '憑證鏈',
        chromeZh: '憑證階層',
        chromeEn: 'Certificate Hierarchy',
        note: 'Windows 是「憑證路徑」分頁（對話框樣板，未收錄）。',
      },
      {
        key: 'critical',
        zh: '關鍵',
        winZh: '關鍵（篩選選項「只有關鍵延伸」）',
        winEn: 'Critical Extensions Only',
        chromeZh: '重要／非重要',
        chromeEn: 'Critical／Not Critical',
        warn: true,
        note: '本站、《基本要求》與 Windows 都用「關鍵」，只有 Chrome 用「重要」。',
      },
      {
        key: '欄位篩選',
        winZh: '<全部>／只有版本 1 的欄位／只有延伸／只有關鍵延伸／只有內容',
        chromeRaw: '無篩選功能',
      },
      {
        key: '檢視器標題',
        winZh: '憑證資訊',
        winEn: 'Certificate Information',
        chromeZh: '憑證檢視者',
        chromeEn: 'Certificate Viewer',
      },
      {
        key: 'basicConstraints 的值',
        zh: 'cA／pathLenConstraint',
        winRaw: 'Subject Type=CA, Path Length Constraint=None',
        chromeZh: '這是憑證授權單位／中繼 CA 數目上限：無限制',
        warn: true,
      },
      {
        key: '憑證用途',
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
    title: 'critical：只有 Chrome 不叫「關鍵」',
    body: '本站與《基本要求》用「關鍵」，Windows 也用「關鍵延伸」，只有 Chrome 用「重要／非重要」。跟客戶說「這個擴充欄位標了關鍵」，他在 Chrome 上找不到「關鍵」兩個字。',
  },
  {
    title: 'Chrome 的「此日期之後／此日期之前」容易讀反',
    body: 'notBefore／notAfter 的語意是「不早於／不晚於」，Chrome 的譯法字面與直覺相反。Windows 的「有效期自／有效期到」直覺得多；對截圖討論有效期前，先問對方看的是哪個檢視器。',
  },
  {
    title: 'extensions 三邊三種講法',
    body: '本站「擴充欄位」、Windows「延伸」、Chrome「擴充功能」。Chrome 那個跟瀏覽器外掛同名，客戶會以為在講外掛。',
  },
  {
    title: 'Windows 的「增強金鑰使用方法 (內容)」不是憑證欄位',
    body: 'extKeyUsage 在 Windows 叫「增強金鑰使用方法」（Enhanced Key Usage，微軟自己的舊稱），Chrome 與本站叫「擴充金鑰使用方法」。Windows 詳細資料另有一列括號標「(內容)」的同名項目，那是本機憑證存放區的設定、不在憑證裡——客戶截這一列來爭論時要先分清楚。',
  },
  {
    title: 'Windows 不翻 keyUsage 位元，卻翻 EKU 值',
    body: '同一個畫面裡，金鑰使用方法的內容是英文（Digital Signature、Key Encipherment…），增強金鑰使用方法的內容卻是中文（伺服器驗證、用戶端驗證）。Chrome 兩邊都翻。同一張憑證在兩個檢視器下看起來像兩份文件。',
  },
  {
    title: 'Chrome 詳細資訊不翻 DN 屬性',
    body: '詳細資訊樹只給 CN／O／OU／L／ST／C 短碼，一般分頁才翻 CN／O／OU 三個。客戶說「上面只有英文縮寫」，通常就是在看詳細資訊樹。',
  },
  {
    title: '發布／發佈、識別碼／識別元',
    body: 'CRL Distribution Points 本站與 Chrome 作「CRL 發布點」，Windows 作「CRL 發佈點」。Windows 同一畫面裡 AKI 是「授權單位金鑰識別元」、SKI 是「主體金鑰識別碼」。',
  },
  {
    title: '廢止／撤銷',
    body: '本站依中華電信 HiPKI CA CP/CPS 用「廢止」（憑證廢止清冊），Windows 用「撤銷清單」「撤銷日期」。客戶講「撤銷」時指的通常就是我們說的廢止。',
  },
  {
    title: 'Chrome 的「X.500 姓名」',
    body: '那是 directoryName（X.500 Name），Chrome 把 Name 當成人名翻了。憑證裡它放的是一個辨別名稱，不是誰的姓名。',
  },
  {
    title: '指紋不是憑證裡的欄位',
    body: 'Windows 的「憑證指紋」與 Chrome 的「SHA-256 指紋」都是檢視器當場算出來的。客戶說「指紋跟你給的不一樣」，先確認兩邊用的是不是同一個雜湊演算法。',
  },
];
