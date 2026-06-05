; ============================================================
;  Windows Controller — Inno Setup o'rnatgich skripti
; ============================================================
;  Avval PyInstaller bilan dastur yig'iladi:
;      pyinstaller installer/WindowsController.spec
;  So'ng shu skriptni Inno Setup Compiler (ISCC) bilan kompilyatsiya qiling:
;      iscc installer\installer.iss
;  Natija:  installer/Output/WindowsController-Setup.exe
;
;  Bu o'rnatgich:
;   - Dasturni Program Files ga o'rnatadi
;   - O'rnatish vaqtida LLM provayder va API kalitni so'raydi
;     va ularni {app}\settings.env fayliga yozadi
;   - Ish stoli yorlig'i va (ixtiyoriy) avtoyuklash (autostart) qo'shadi
; ============================================================

#define MyAppName "Windows Controller"
#define MyAppVersion "1.0.0"
#define MyAppPublisher "Windows Controller"
#define MyAppExeName "WindowsController.exe"

[Setup]
; AppId — dastur uchun noyob identifikator (o'zgartirmang)
AppId={{8F3A2C71-4B9E-4D2A-9C1F-7E6D5A4B3C21}
AppName={#MyAppName}
AppVersion={#MyAppVersion}
AppPublisher={#MyAppPublisher}
DefaultDirName={autopf}\WindowsController
DefaultGroupName={#MyAppName}
DisableProgramGroupPage=yes
OutputDir=Output
OutputBaseFilename=WindowsController-Setup
Compression=lzma2
SolidCompression=yes
WizardStyle=modern
; 64-bitli Windows uchun
ArchitecturesAllowed=x64compatible
ArchitecturesInstallIn64BitMode=x64compatible
; settings.env ni Program Files ga yozish uchun admin huquqi kerak
PrivilegesRequired=admin
; SetupIconFile=app.ico
UninstallDisplayName={#MyAppName}

[Languages]
Name: "english"; MessagesFile: "compiler:Default.isl"

[Tasks]
Name: "desktopicon"; Description: "Ish stolida yorliq yaratish"; GroupDescription: "Qo'shimcha yorliqlar:"
Name: "startupicon"; Description: "Windows ishga tushganda dasturni avtomatik ishga tushirish"; GroupDescription: "Avtoyuklash:"

[Files]
; PyInstaller yaratgan butun papkani ko'chiramiz
Source: "..\dist\WindowsController\*"; DestDir: "{app}"; Flags: recursesubdirs createallsubdirs ignoreversion

[Icons]
Name: "{group}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"
Name: "{group}\{#MyAppName} ni o'chirish"; Filename: "{uninstallexe}"
Name: "{autodesktop}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; Tasks: desktopicon
; Avtoyuklash uchun Startup papkasiga yorliq
Name: "{userstartup}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; Tasks: startupicon

[Run]
Filename: "{app}\{#MyAppExeName}"; Description: "Dasturni hozir ishga tushirish"; Flags: nowait postinstall skipifsilent

[UninstallDelete]
; O'chirishda sozlamalar faylini ham olib tashlaymiz
Type: files; Name: "{app}\settings.env"

; ============================================================
;  Pascal Script — API kalit so'raydigan maxsus sahifalar
; ============================================================
[Code]
var
  ProviderPage: TInputOptionWizardPage;
  ApiKeyPage:   TInputQueryWizardPage;

procedure InitializeWizard;
begin
  { 1-sahifa: LLM provayderni tanlash (radio tugmalar) }
  ProviderPage := CreateInputOptionPage(
    wpSelectTasks,
    'Sun''iy intellekt provayderi',
    'Qaysi xizmatdan foydalanasiz?',
    'Buyruqlarni tushunish uchun ishlatiladigan LLM xizmatini tanlang:',
    True,   { exclusive — faqat bittasini tanlash mumkin }
    False
  );
  ProviderPage.Add('Google Gemini');
  ProviderPage.Add('OpenAI (ChatGPT)');
  ProviderPage.SelectedValueIndex := 0;  { standart: Gemini }

  { 2-sahifa: API kalitni kiritish }
  ApiKeyPage := CreateInputQueryPage(
    ProviderPage.ID,
    'API kaliti',
    'Maxfiy kalitingizni kiriting',
    'Tanlangan xizmatning API kalitini kiriting. ' +
    'Kalit kompyuteringizda settings.env fayliga saqlanadi va boshqa joyga yuborilmaydi.'
  );
  { Password=True -> kalit yulduzcha (*) bilan ko'rsatiladi }
  ApiKeyPage.Add('API kaliti:', True);
end;

{ Foydalanuvchi API kalitni kiritmasa, ogohlantiramiz (lekin davom etishga ruxsat) }
function NextButtonClick(CurPageID: Integer): Boolean;
begin
  Result := True;
  if CurPageID = ApiKeyPage.ID then
  begin
    if Trim(ApiKeyPage.Values[0]) = '' then
    begin
      if MsgBox('API kaliti kiritilmadi. Kalitsiz dastur ovozli/aqlli ' +
                'buyruqlarni tushuna olmaydi. Baribir davom etasizmi?',
                mbConfirmation, MB_YESNO) = IDNO then
        Result := False;
    end;
  end;
end;

{ O'rnatish tugagach settings.env faylini yozamiz }
procedure CurStepChanged(CurStep: TSetupStep);
var
  Provider: String;
  ApiKey:   String;
  Content:  String;
  FilePath: String;
begin
  if CurStep = ssPostInstall then
  begin
    if ProviderPage.SelectedValueIndex = 1 then
      Provider := 'openai'
    else
      Provider := 'gemini';

    ApiKey := Trim(ApiKeyPage.Values[0]);

    Content :=
      '# Windows Controller sozlamalari (o''rnatgich tomonidan yaratilgan)' + #13#10 +
      'WC_LLM_PROVIDER=' + Provider + #13#10 +
      'WC_API_KEY=' + ApiKey + #13#10;

    FilePath := ExpandConstant('{app}\settings.env');
    if not SaveStringToFile(FilePath, Content, False) then
      MsgBox('Diqqat: settings.env faylini yozib bo''lmadi. ' +
             'Keyinroq qo''lda yaratishingiz mumkin.', mbError, MB_OK);
  end;
end;
