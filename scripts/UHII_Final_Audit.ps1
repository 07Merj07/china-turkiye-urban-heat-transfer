# UHII Final Dataset Audit
# Place this script in the project's scripts folder.
# It detects the project root automatically and does not change or delete source data.
# Audit reports are written to data\audit_reports.

$ErrorActionPreference = 'Stop'
$root = Split-Path -Parent $PSScriptRoot
$dataDir = Join-Path $root 'data'
$datasetDir = Join-Path $dataDir 'UHII_dataset'
$cityInfoPath = Join-Path $dataDir 'CityInfo.csv'
$mappingPath = Join-Path $dataDir 'CityInfo_with_Country.csv'
$outputDir = Join-Path $dataDir 'audit_reports'

if (-not (Test-Path $datasetDir)) { throw "Dataset folder not found: $datasetDir. Check that this script is in the project's scripts folder and that data\UHII_dataset exists." }
if (-not (Test-Path $cityInfoPath)) { throw "Reference file not found: $cityInfoPath" }
if (-not (Test-Path $mappingPath)) { throw "Country mapping file not found: $mappingPath" }
New-Item -ItemType Directory -Path $outputDir -Force | Out-Null

Write-Host "[1/4] Loading and checking the two reference files..." -ForegroundColor Cyan
$cityRows = @(Import-Csv -LiteralPath $cityInfoPath -Encoding UTF8)
$mappingRows = @(Import-Csv -LiteralPath $mappingPath -Encoding UTF8)
if ($cityRows.Count -eq 0 -or $mappingRows.Count -eq 0) { throw 'A reference file is empty or could not be read.' }

$expectedIds = [System.Collections.Generic.HashSet[string]]::new([System.StringComparer]::Ordinal)
$cityIds = [System.Collections.Generic.HashSet[string]]::new([System.StringComparer]::Ordinal)
$countryById = [System.Collections.Generic.Dictionary[string,string]]::new([System.StringComparer]::Ordinal)
$mappingRowById = [System.Collections.Generic.Dictionary[string,object]]::new([System.StringComparer]::Ordinal)
$cityDuplicateRows = 0; $cityBlankIds = 0
foreach ($row in $cityRows) {
    $id = [string]$row.UrbanId
    if ($null -eq $id) { $id = '' } else { $id = $id.Trim() }
    if ([string]::IsNullOrWhiteSpace($id)) { $cityBlankIds++; continue }
    if (-not $cityIds.Add($id)) { $cityDuplicateRows++ }
}

$mappingDuplicateRows = 0; $mappingBlankIds = 0
$chinaCount = 0; $turkiyeCount = 0; $blankCountryCount = 0; $otherCountryCount = 0
foreach ($row in $mappingRows) {
    $id = [string]$row.UrbanId
    if ($null -eq $id) { $id = '' } else { $id = $id.Trim() }
    $country = [string]$row.Country
    if ($null -eq $country) { $country = '' } else { $country = $country.Trim() }
    if ([string]::IsNullOrWhiteSpace($id)) { $mappingBlankIds++; continue }
    if (-not $expectedIds.Add($id)) { $mappingDuplicateRows++ }
    $countryById[$id] = $country
    $mappingRowById[$id] = $row
    if ($country -eq 'China') { $chinaCount++ }
    elseif ($country -eq 'Türkiye') { $turkiyeCount++ }
    elseif ([string]::IsNullOrWhiteSpace($country)) { $blankCountryCount++ }
    else { $otherCountryCount++ }
}

$idsOnlyInMapping = 0
foreach ($id in $expectedIds) { if (-not $cityIds.Contains($id)) { $idsOnlyInMapping++ } }
$idsOnlyInCityInfo = 0
foreach ($id in $cityIds) { if (-not $expectedIds.Contains($id)) { $idsOnlyInCityInfo++ } }

$coordinateColumns = @('Longitude','Latitude','Area')
$coordinateCompared = 0; $coordinateMismatchCells = 0; $coordinateCompareAvailable = $true
foreach ($col in $coordinateColumns) {
    if (-not ($cityRows[0].PSObject.Properties.Name -contains $col) -or -not ($mappingRows[0].PSObject.Properties.Name -contains $col)) {
        $coordinateCompareAvailable = $false
    }
}
if ($coordinateCompareAvailable) {
    $cityRowById = [System.Collections.Generic.Dictionary[string,object]]::new([System.StringComparer]::Ordinal)
    foreach ($row in $cityRows) {
        $id = [string]$row.UrbanId
        if ($null -ne $id) { $id = $id.Trim() }
        if (-not [string]::IsNullOrWhiteSpace($id) -and -not $cityRowById.ContainsKey($id)) { $cityRowById[$id] = $row }
    }
    $culture = [System.Globalization.CultureInfo]::InvariantCulture
    foreach ($id in $expectedIds) {
        if (-not $cityRowById.ContainsKey($id) -or -not $mappingRowById.ContainsKey($id)) { continue }
        foreach ($col in $coordinateColumns) {
            $a = [string]$cityRowById[$id].$col
            $b = [string]$mappingRowById[$id].$col
            $av = 0.0; $bv = 0.0
            $okA = [double]::TryParse($a, [System.Globalization.NumberStyles]::Float, $culture, [ref]$av)
            $okB = [double]::TryParse($b, [System.Globalization.NumberStyles]::Float, $culture, [ref]$bv)
            $coordinateCompared++
            if (-not $okA -or -not $okB -or [math]::Abs($av - $bv) -gt 0.000001) { $coordinateMismatchCells++ }
        }
    }
}

$mappingAuditPath = Join-Path $outputDir 'UHII_Final_Mapping_Audit.csv'
$cityRowsStatus = if ($cityRows.Count -eq 10196) { 'PASS' } else { 'REVIEW' }
$cityUniqueStatus = if ($cityDuplicateRows -eq 0 -and $cityBlankIds -eq 0) { 'PASS' } else { 'REVIEW' }
$mappingRowsStatus = if ($mappingRows.Count -eq 10196) { 'PASS' } else { 'REVIEW' }
$mappingUniqueStatus = if ($mappingDuplicateRows -eq 0 -and $mappingBlankIds -eq 0) { 'PASS' } else { 'REVIEW' }
$idsMappingStatus = if ($idsOnlyInMapping -eq 0) { 'PASS' } else { 'REVIEW' }
$idsCityStatus = if ($idsOnlyInCityInfo -eq 0) { 'PASS' } else { 'REVIEW' }
$chinaStatus = if ($chinaCount -eq 1441) { 'PASS' } else { 'REVIEW' }
$turkiyeStatus = if ($turkiyeCount -eq 180) { 'PASS' } else { 'REVIEW' }
$coordinateStatus = if (-not $coordinateCompareAvailable) { 'NOT CHECKED' } elseif ($coordinateMismatchCells -eq 0) { 'PASS' } else { 'REVIEW' }
$coordinateValue = if (-not $coordinateCompareAvailable) { 'N/A' } else { [string]$coordinateMismatchCells }
$coordinateNotes = if (-not $coordinateCompareAvailable) { 'Longitude, Latitude and Area columns were not all available in both files.' } else { "Compared $coordinateCompared metadata cells using 1e-6 tolerance." }
$mappingAuditRows = @(
    [PSCustomObject]@{Check='CityInfo rows'; Status=$cityRowsStatus; Value=$cityRows.Count; Notes='Expected reference row count based on the existing project audit: 10196.'},
    [PSCustomObject]@{Check='CityInfo unique IDs'; Status=$cityUniqueStatus; Value=$cityIds.Count; Notes="Duplicate ID rows=$cityDuplicateRows; blank IDs=$cityBlankIds."},
    [PSCustomObject]@{Check='Country mapping rows'; Status=$mappingRowsStatus; Value=$mappingRows.Count; Notes='Expected row count based on the existing project audit: 10196.'},
    [PSCustomObject]@{Check='Country mapping unique IDs'; Status=$mappingUniqueStatus; Value=$expectedIds.Count; Notes="Duplicate ID rows=$mappingDuplicateRows; blank IDs=$mappingBlankIds."},
    [PSCustomObject]@{Check='IDs only in CityInfo_with_Country'; Status=$idsMappingStatus; Value=$idsOnlyInMapping; Notes='Mapping IDs absent from CityInfo.csv.'},
    [PSCustomObject]@{Check='IDs only in CityInfo'; Status=$idsCityStatus; Value=$idsOnlyInCityInfo; Notes='CityInfo.csv IDs absent from the country mapping.'},
    [PSCustomObject]@{Check='China country labels'; Status=$chinaStatus; Value=$chinaCount; Notes='Expected main-sample count from the current project mapping audit: 1441.'},
    [PSCustomObject]@{Check='Türkiye country labels'; Status=$turkiyeStatus; Value=$turkiyeCount; Notes='Expected main-sample count from the current project mapping audit: 180.'},
    [PSCustomObject]@{Check='Blank country labels'; Status='INFO'; Value=$blankCountryCount; Notes='Blank labels are not automatically errors; retain them as unmatched unless resolved with defensible geography.'},
    [PSCustomObject]@{Check='Other country labels'; Status='INFO'; Value=$otherCountryCount; Notes='All country labels other than China, Türkiye and blank.'},
    [PSCustomObject]@{Check='Coordinate/area metadata comparison'; Status=$coordinateStatus; Value=$coordinateValue; Notes=$coordinateNotes}
)
$mappingAuditRows | Export-Csv -LiteralPath $mappingAuditPath -NoTypeInformation -Encoding UTF8

Write-Host ("Mapping check: CityInfo IDs={0}; mapped IDs={1}; China={2}; Türkiye={3}; ID set differences={4}/{5}." -f $cityIds.Count,$expectedIds.Count,$chinaCount,$turkiyeCount,$idsOnlyInMapping,$idsOnlyInCityInfo)
Write-Host '[2/4] Starting one-pass scan of all UHII CSV files. Source data will not be changed...' -ForegroundColor Cyan
# Coverage is appended during the scan, so remove any report from an earlier run.
Remove-Item -LiteralPath (Join-Path $outputDir 'UHII_Final_Coverage_Audit.csv') -ErrorAction SilentlyContinue

if (-not ('UHII_FinalAuditEngine' -as [type])) {
$cs = @'
using System;
using System.IO;
using System.Text;
using System.Collections.Generic;
using System.Globalization;

public static class UHII_FinalAuditEngine {
    private static readonly string[] Methods = new string[] { "Intensity_EA", "Intensity_IEA", "Intensity_MEA", "Intensity_DEA" };
    private static readonly string[] MethodShort = new string[] { "EA", "IEA", "MEA", "DEA" };
    private static readonly string[] Diurnal = new string[] { "Day", "Nig" };
    private static readonly int[] Codes = new int[] { 1,2,3,4,5,6,7,8,9,10,11,12,21,22,23,24,30 };
    private class Stats {
        public long Rows, Malformed, DuplicateIds, BlankIds, UnknownIds, MissingIds, ChinaRows, TurkeyRows, ChinaCities, TurkeyCities;
        public long[] NA = new long[4], Blank = new long[4], Invalid = new long[4], NonFinite = new long[4], Valid = new long[4];
        public double[] Min = new double[4], Max = new double[4];
        public long[,] CountryNA = new long[2,4];
        public long[] CountryRows = new long[2], CountryCities = new long[2];
        public HashSet<string>[] CountrySeen = new HashSet<string>[2];
        public Stats() { for(int i=0;i<4;i++){ Min[i]=Double.PositiveInfinity; Max[i]=Double.NegativeInfinity; } CountrySeen[0]=new HashSet<string>(StringComparer.Ordinal); CountrySeen[1]=new HashSet<string>(StringComparer.Ordinal); }
    }
    private class RangeStats { public long Valid, NA, Blank, Invalid, NonFinite; public double Min=Double.PositiveInfinity, Max=Double.NegativeInfinity; public HashSet<string> Files=new HashSet<string>(StringComparer.Ordinal); }
    private static string Q(string s) { if(s==null) s=""; if(s.IndexOf('"')>=0) s=s.Replace("\"","\"\""); if(s.IndexOf(',')>=0 || s.IndexOf('"')>=0 || s.IndexOf('\n')>=0 || s.IndexOf('\r')>=0) return "\""+s+"\""; return s; }
    private static void Row(StreamWriter w, params string[] fields) { for(int i=0;i<fields.Length;i++){ if(i>0) w.Write(','); w.Write(Q(fields[i])); } w.WriteLine(); }
    private static string Num(long v) { return v.ToString(CultureInfo.InvariantCulture); }
    private static string Dbl(double v) { return (Double.IsInfinity(v) || Double.IsNaN(v)) ? "" : v.ToString("G17", CultureInfo.InvariantCulture); }
    private static int IndexOf(string[] items, string val) { for(int i=0;i<items.Length;i++) if(String.Equals(items[i].Trim().TrimStart('\uFEFF'),val,StringComparison.Ordinal)) return i; return -1; }
    private static string[] ParseCsv(string line, out bool malformed) {
        malformed=false;
        if(line.IndexOf('"')<0) return line.Split(',');
        List<string> fields=new List<string>(); StringBuilder b=new StringBuilder(); bool quoted=false;
        for(int i=0;i<line.Length;i++) {
            char c=line[i];
            if(c=='"') {
                if(quoted && i+1<line.Length && line[i+1]=='"') { b.Append('"'); i++; }
                else if(quoted) quoted=false;
                else if(b.Length==0) quoted=true;
                else malformed=true;
            } else if(c==',' && !quoted) { fields.Add(b.ToString()); b.Length=0; }
            else b.Append(c);
        }
        if(quoted) malformed=true;
        fields.Add(b.ToString()); return fields.ToArray();
    }
    private static int CountryIndex(string country) { if(String.Equals(country,"China",StringComparison.Ordinal)) return 0; if(String.Equals(country,"Türkiye",StringComparison.Ordinal)) return 1; return -1; }
    private static void Issue(StreamWriter issues, string file, string kind, long count, string detail) { if(count>0) Row(issues,file,kind,Num(count),detail); }

    public static void Run(string folder, string outputDir, Dictionary<string,string> countryById, HashSet<string> expectedIds, int expectedRows) {
        string fileOut=Path.Combine(outputDir,"UHII_Final_File_Audit.csv");
        string countryOut=Path.Combine(outputDir,"UHII_Final_Country_NA_Audit.csv");
        string issueOut=Path.Combine(outputDir,"UHII_Final_Audit_Issues.csv");
        string coverageOut=Path.Combine(outputDir,"UHII_Final_Coverage_Audit.csv");
        string rangesOut=Path.Combine(outputDir,"UHII_Final_Value_Ranges.csv");
        string[] files=Directory.GetFiles(folder,"*.csv",SearchOption.TopDirectoryOnly); Array.Sort(files,StringComparer.OrdinalIgnoreCase);
        Dictionary<string,int> comboCounts=new Dictionary<string,int>(StringComparer.OrdinalIgnoreCase);
        Dictionary<string,RangeStats> allRanges=new Dictionary<string,RangeStats>(StringComparer.Ordinal);
        using(StreamWriter fw=new StreamWriter(fileOut,false,new UTF8Encoding(true)))
        using(StreamWriter cw=new StreamWriter(countryOut,false,new UTF8Encoding(true)))
        using(StreamWriter iw=new StreamWriter(issueOut,false,new UTF8Encoding(true))) {
            Row(fw,"File","FilenameOK","Indicator","Period","Year","Code","Rows","HeaderOK","MalformedRows","UniqueIDs","DuplicateIDRows","BlankIDs","UnknownIDs","MissingExpectedIDs","ChinaCities","TurkeyCities",
                "NA_EA","NA_IEA","NA_MEA","NA_DEA","Blank_EA","Blank_IEA","Blank_MEA","Blank_DEA","Invalid_EA","Invalid_IEA","Invalid_MEA","Invalid_DEA","NonFinite_EA","NonFinite_IEA","NonFinite_MEA","NonFinite_DEA","Valid_EA","Valid_IEA","Valid_MEA","Valid_DEA",
                "Min_EA","Max_EA","Min_IEA","Max_IEA","Min_MEA","Max_MEA","Min_DEA","Max_DEA");
            Row(cw,"File","Country","MatchedCities","RowsChecked","CellsChecked","NA_Count","NA_EA","NA_IEA","NA_MEA","NA_DEA");
            Row(iw,"File","Issue","Count","Details");
            int index=0;
            foreach(string path in files) {
                index++; if(index%100==0) { Console.WriteLine("Scanning CSV files: "+index+" / "+files.Length); }
                string name=Path.GetFileName(path); string stem=Path.GetFileNameWithoutExtension(path); string[] fp=stem.Split('_');
                string indicator=fp.Length>0?fp[0]:""; string period=fp.Length>1?fp[1]:""; int year=0, code=0;
                bool yearOK=fp.Length==4 && Int32.TryParse(fp[2],NumberStyles.Integer,CultureInfo.InvariantCulture,out year);
                bool codeOK=fp.Length==4 && Int32.TryParse(fp[3],NumberStyles.Integer,CultureInfo.InvariantCulture,out code);
                bool filenameOK=fp.Length==4 && yearOK && codeOK && (period=="Day" || period=="Nig") && Array.IndexOf(Codes,code)>=0;
                if(!filenameOK) Issue(iw,name,"FilenameFormat",1,"Expected Indicator_Day-or-Nig_Year_Code.csv with code 1-12, 21-24 or 30.");
                if(fp.Length==4 && yearOK && codeOK && (period=="Day" || period=="Nig")) {
                    string key=indicator+"|"+period+"|"+year.ToString(CultureInfo.InvariantCulture)+"|"+code.ToString(CultureInfo.InvariantCulture);
                    if(!comboCounts.ContainsKey(key)) comboCounts[key]=0; comboCounts[key]++;
                }
                Stats s=new Stats(); bool headerOK=false; int idIx=-1; int[] mIx=new int[4]; for(int j=0;j<4;j++)mIx[j]=-1; long uniqueIds=0;
                HashSet<string> seen=new HashSet<string>(StringComparer.Ordinal); string[] firstInvalid=new string[4];
                try {
                    using(StreamReader reader=new StreamReader(path,Encoding.UTF8,true)) {
                        string line=reader.ReadLine();
                        if(line==null) { Issue(iw,name,"EmptyFile",1,"File has no header line."); }
                        else {
                            bool headerMalformed=false; string[] header=ParseCsv(line,out headerMalformed);
                            idIx=IndexOf(header,"UrbanId"); for(int j=0;j<4;j++)mIx[j]=IndexOf(header,Methods[j]);
                            headerOK=idIx>=0; for(int j=0;j<4;j++) if(mIx[j]<0) headerOK=false;
                            if(!headerOK) Issue(iw,name,"MissingRequiredColumn",1,"Required columns: UrbanId, Intensity_EA, Intensity_IEA, Intensity_MEA, Intensity_DEA.");
                            if(headerMalformed) Issue(iw,name,"MalformedHeaderQuotes",1,"Header quote syntax could not be parsed cleanly.");
                            while((line=reader.ReadLine())!=null) {
                                s.Rows++;
                                bool rowMalformed=false; string[] p=ParseCsv(line,out rowMalformed);
                                if(rowMalformed || p.Length!=header.Length) s.Malformed++;
                                string id=(idIx>=0 && idIx<p.Length)?p[idIx].Trim():"";
                                if(String.IsNullOrWhiteSpace(id)) s.BlankIds++;
                                bool isNew=false;
                                if(!String.IsNullOrWhiteSpace(id)) {
                                    isNew=seen.Add(id);
                                    if(!isNew) s.DuplicateIds++;
                                    if(!expectedIds.Contains(id)) { if(isNew) s.UnknownIds++; }
                                    string country=""; int ci=-1;
                                    if(countryById.TryGetValue(id,out country)) ci=CountryIndex(country);
                                    if(isNew && ci==0) s.ChinaCities++;
                                    if(isNew && ci==1) s.TurkeyCities++;
                                    if(ci>=0) {
                                        s.CountryRows[ci]++;
                                        if(ci==0)s.ChinaRows++; else s.TurkeyRows++;
                                        for(int j=0;j<4;j++) {
                                            string value=mIx[j]>=0 && mIx[j]<p.Length ? p[mIx[j]].Trim() : "";
                                            if(String.Equals(value,"NA",StringComparison.OrdinalIgnoreCase)) s.CountryNA[ci,j]++;
                                        }
                                    }
                                }
                                for(int j=0;j<4;j++) {
                                    string value=mIx[j]>=0 && mIx[j]<p.Length ? p[mIx[j]].Trim() : "";
                                    if(String.Equals(value,"NA",StringComparison.OrdinalIgnoreCase)) s.NA[j]++;
                                    else if(String.IsNullOrWhiteSpace(value)) s.Blank[j]++;
                                    else {
                                        double v;
                                        if(Double.TryParse(value,NumberStyles.Float,CultureInfo.InvariantCulture,out v)) {
                                            if(Double.IsNaN(v) || Double.IsInfinity(v)) s.NonFinite[j]++;
                                            else { s.Valid[j]++; if(v<s.Min[j])s.Min[j]=v; if(v>s.Max[j])s.Max[j]=v; }
                                        } else { s.Invalid[j]++; if(firstInvalid[j]==null)firstInvalid[j]=value; }
                                    }
                                }
                            }
                        }
                    }
                } catch(Exception ex) { Issue(iw,name,"ReadError",1,ex.GetType().Name+": "+ex.Message); }
                uniqueIds=seen.Count;
                foreach(string id in expectedIds) if(!seen.Contains(id)) s.MissingIds++;
                if(s.Rows!=expectedRows) Issue(iw,name,"WrongRowCount",Math.Abs(s.Rows-expectedRows),"Rows found="+s.Rows+"; expected="+expectedRows+".");
                Issue(iw,name,"MalformedRows",s.Malformed,"Rows whose field count differs from the header or have malformed quote syntax.");
                Issue(iw,name,"BlankIDs",s.BlankIds,"Rows with missing UrbanId.");
                Issue(iw,name,"DuplicateIDRows",s.DuplicateIds,"Repeated UrbanId rows within this file.");
                Issue(iw,name,"UnexpectedIDs",s.UnknownIds,"Distinct UrbanId values absent from CityInfo_with_Country.csv.");
                Issue(iw,name,"MissingExpectedIDs",s.MissingIds,"Reference UrbanId values absent from this file.");
                if(s.ChinaCities!=1441) Issue(iw,name,"ChinaCityCountMismatch",Math.Abs(s.ChinaCities-1441),"Distinct mapped China IDs found="+s.ChinaCities+"; expected 1441.");
                if(s.TurkeyCities!=180) Issue(iw,name,"TürkiyeCityCountMismatch",Math.Abs(s.TurkeyCities-180),"Distinct mapped Türkiye IDs found="+s.TurkeyCities+"; expected 180.");
                for(int j=0;j<4;j++) {
                    Issue(iw,name,"BlankMeasurements_"+MethodShort[j],s.Blank[j],"Blank/whitespace cells in "+Methods[j]+".");
                    Issue(iw,name,"InvalidNumeric_"+MethodShort[j],s.Invalid[j],"Non-numeric value examples: "+(firstInvalid[j]??"none"));
                    Issue(iw,name,"NonFiniteNumeric_"+MethodShort[j],s.NonFinite[j],"NaN or Infinity values in "+Methods[j]+".");
                    string rk=indicator+"|"+MethodShort[j]; RangeStats r;
                    if(!allRanges.TryGetValue(rk,out r)){r=new RangeStats();allRanges[rk]=r;}
                    r.Files.Add(name); r.Valid+=s.Valid[j]; r.NA+=s.NA[j]; r.Blank+=s.Blank[j]; r.Invalid+=s.Invalid[j]; r.NonFinite+=s.NonFinite[j];
                    if(s.Min[j]<r.Min)r.Min=s.Min[j]; if(s.Max[j]>r.Max)r.Max=s.Max[j];
                }
                if(fp.Length==4 && yearOK && codeOK && (period=="Day" || period=="Nig")) {
                    bool indicatorKnown=(indicator=="Mod1"||indicator=="Mod2"||indicator=="AMod2"||indicator=="SAT"||indicator=="SMod2"||indicator=="Myd1"||indicator=="Myd2"||indicator=="SMyd1");
                    int start=2001,end=2021;
                    if(indicator=="AMod2"||indicator=="SAT"||indicator=="SMod2"){start=2001;end=2020;}
                    else if(indicator=="Myd1"||indicator=="Myd2"){start=2003;end=2021;}
                    else if(indicator=="SMyd1"){start=2003;end=2020;}
                    if(!indicatorKnown || year<start || year>end || Array.IndexOf(Codes,code)<0) Issue(iw,name,"UnexpectedFileCombination",1,"Indicator/year/period/code is outside the project's configured coverage.");
                }
                List<string> f=new List<string>();
                f.Add(name); f.Add(filenameOK.ToString()); f.Add(indicator); f.Add(period); f.Add(year.ToString(CultureInfo.InvariantCulture)); f.Add(code.ToString(CultureInfo.InvariantCulture)); f.Add(Num(s.Rows)); f.Add(headerOK.ToString()); f.Add(Num(s.Malformed)); f.Add(Num(uniqueIds)); f.Add(Num(s.DuplicateIds)); f.Add(Num(s.BlankIds)); f.Add(Num(s.UnknownIds)); f.Add(Num(s.MissingIds)); f.Add(Num(s.ChinaCities)); f.Add(Num(s.TurkeyCities));
                for(int j=0;j<4;j++)f.Add(Num(s.NA[j])); for(int j=0;j<4;j++)f.Add(Num(s.Blank[j])); for(int j=0;j<4;j++)f.Add(Num(s.Invalid[j])); for(int j=0;j<4;j++)f.Add(Num(s.NonFinite[j])); for(int j=0;j<4;j++)f.Add(Num(s.Valid[j]));
                for(int j=0;j<4;j++){ f.Add(Dbl(s.Min[j])); f.Add(Dbl(s.Max[j])); }
                Row(fw,f.ToArray());
                for(int ci=0;ci<2;ci++) {
                    string country=ci==0?"China":"Türkiye"; long naTotal=0; for(int j=0;j<4;j++)naTotal+=s.CountryNA[ci,j];
                    Row(cw,name,country,Num(ci==0?s.ChinaCities:s.TurkeyCities),Num(s.CountryRows[ci]),Num(s.CountryRows[ci]*4),Num(naTotal),Num(s.CountryNA[ci,0]),Num(s.CountryNA[ci,1]),Num(s.CountryNA[ci,2]),Num(s.CountryNA[ci,3]));
                }
            }
            Console.WriteLine("CSV scan finished: "+files.Length+" files.");
        }
        using(StreamWriter iw=new StreamWriter(issueOut,true,new UTF8Encoding(true))) {
            Dictionary<string,int> ranges=new Dictionary<string,int>(StringComparer.Ordinal) {
                {"Mod1",21},{"Mod2",21},{"AMod2",20},{"SAT",20},{"SMod2",20},{"Myd1",19},{"Myd2",19},{"SMyd1",18}
            };
            foreach(KeyValuePair<string,int> kv in ranges) {
                int start=(kv.Key=="Myd1"||kv.Key=="Myd2"||kv.Key=="SMyd1")?2003:2001;
                int end=start+kv.Value-1;
                foreach(int y in YearRange(start,end)) foreach(string p in Diurnal) {
                    int actual=0; List<string> missing=new List<string>(); List<string> duplicate=new List<string>();
                    foreach(int c in Codes) {
                        string key=kv.Key+"|"+p+"|"+y.ToString(CultureInfo.InvariantCulture)+"|"+c.ToString(CultureInfo.InvariantCulture);
                        int count=comboCounts.ContainsKey(key)?comboCounts[key]:0; actual+=count;
                        if(count==0)missing.Add(c.ToString(CultureInfo.InvariantCulture)); if(count>1)duplicate.Add(c.ToString(CultureInfo.InvariantCulture)+"(x"+count+")");
                    }
                    RowCoverage(coverageOut,kv.Key,y,p,17,actual,String.Join(";",missing.ToArray()),String.Join(";",duplicate.ToArray()));
                    if(missing.Count>0) Row(iw,"", "MissingCoverageFiles",missing.Count.ToString(CultureInfo.InvariantCulture),"Indicator="+kv.Key+"; Year="+y+"; Period="+p+"; Missing codes="+String.Join(";",missing.ToArray()));
                    if(duplicate.Count>0) Row(iw,"", "DuplicateCoverageCombinations",duplicate.Count.ToString(CultureInfo.InvariantCulture),"Indicator="+kv.Key+"; Year="+y+"; Period="+p+"; Duplicate codes="+String.Join(";",duplicate.ToArray()));
                }
            }
        }
        using(StreamWriter rw=new StreamWriter(rangesOut,false,new UTF8Encoding(true))) {
            Row(rw,"Indicator","Method","FilesSeen","ValidNumericCells","NACells","BlankCells","OtherInvalidCells","NonFiniteCells","Minimum","Maximum","InterpretationNote");
            foreach(KeyValuePair<string,RangeStats> kv in allRanges) {
                string[] bits=kv.Key.Split('|'); RangeStats r=kv.Value;
                Row(rw,bits[0],bits[1],Num(r.Files.Count),Num(r.Valid),Num(r.NA),Num(r.Blank),Num(r.Invalid),Num(r.NonFinite),Dbl(r.Min),Dbl(r.Max),"Range is descriptive across monthly, seasonal and annual files; these time scales overlap and are not independent observations.");
            }
        }
    }
    private static IEnumerable<int> YearRange(int start,int end) { for(int y=start;y<=end;y++) yield return y; }
    private static void RowCoverage(string path,string indicator,int year,string period,int expected,int actual,string missing,string duplicate) {
        bool complete=actual==expected && missing.Length==0 && duplicate.Length==0;
        using(StreamWriter w=new StreamWriter(path,File.Exists(path),new UTF8Encoding(true))) {
            if(w.BaseStream.Length==0) Row(w,"Indicator","Year","Period","ExpectedFiles","ActualFiles","MissingCodes","DuplicateCodes","CoverageComplete");
            Row(w,indicator,year.ToString(CultureInfo.InvariantCulture),period,expected.ToString(CultureInfo.InvariantCulture),actual.ToString(CultureInfo.InvariantCulture),missing,duplicate,complete.ToString());
        }
    }
}
'@
    Add-Type -TypeDefinition $cs -Language CSharp
}

$expectedRowCount = 10196
[UHII_FinalAuditEngine]::Run($datasetDir, $outputDir, $countryById, $expectedIds, $expectedRowCount)

Write-Host '[3/4] Summarizing results and country-level missingness...' -ForegroundColor Cyan
$fileAuditPath = Join-Path $outputDir 'UHII_Final_File_Audit.csv'
$countryAuditPath = Join-Path $outputDir 'UHII_Final_Country_NA_Audit.csv'
$coveragePath = Join-Path $outputDir 'UHII_Final_Coverage_Audit.csv'
$issuePath = Join-Path $outputDir 'UHII_Final_Audit_Issues.csv'
$rangePath = Join-Path $outputDir 'UHII_Final_Value_Ranges.csv'
$summaryPath = Join-Path $outputDir 'UHII_Final_Audit_Summary.txt'
$fileAudit = @(Import-Csv -LiteralPath $fileAuditPath -Encoding UTF8)
$countryAudit = @(Import-Csv -LiteralPath $countryAuditPath -Encoding UTF8)
$coverageAudit = @(Import-Csv -LiteralPath $coveragePath -Encoding UTF8)
$issues = @(Import-Csv -LiteralPath $issuePath -Encoding UTF8)
$ranges = @(Import-Csv -LiteralPath $rangePath -Encoding UTF8)

function Sum-Column([object[]]$Rows, [string]$Column) {
    $s = [long]0
    foreach ($r in $Rows) { $value = 0L; if ([long]::TryParse([string]$r.$Column, [ref]$value)) { $s += $value } }
    return $s
}
function Count-Where([object[]]$Rows, [scriptblock]$Predicate) { return @($Rows | Where-Object $Predicate).Count }

$wrongRows = Count-Where $fileAudit { [long]$_.Rows -ne $expectedRowCount }
$badHeaders = Count-Where $fileAudit { $_.HeaderOK -ne 'True' }
$malformedRows = Sum-Column $fileAudit 'MalformedRows'
$duplicateIDRows = Sum-Column $fileAudit 'DuplicateIDRows'
$blankIDs = Sum-Column $fileAudit 'BlankIDs'
$unknownIDs = Sum-Column $fileAudit 'UnknownIDs'
$missingExpectedIDs = Sum-Column $fileAudit 'MissingExpectedIDs'
$readErrors = Count-Where $issues { $_.Issue -eq 'ReadError' }
$badHeaderSyntax = Count-Where $issues { $_.Issue -eq 'MalformedHeaderQuotes' -or $_.Issue -eq 'EmptyFile' }
$countryCountIssues = Count-Where $issues { $_.Issue -eq 'ChinaCityCountMismatch' -or $_.Issue -eq 'TürkiyeCityCountMismatch' }
$filenameIssues = Count-Where $issues { $_.Issue -eq 'FilenameFormat' -or $_.Issue -eq 'UnexpectedFileCombination' }
$coverageGaps = Count-Where $coverageAudit { $_.CoverageComplete -ne 'True' }
$mappingSetDiff = $idsOnlyInMapping + $idsOnlyInCityInfo
$mappingReferenceProblems = $cityDuplicateRows + $cityBlankIds + $mappingDuplicateRows + $mappingBlankIds + $mappingSetDiff + $coordinateMismatchCells + [int](-not $coordinateCompareAvailable) + [math]::Abs($cityRows.Count - 10196) + [math]::Abs($mappingRows.Count - 10196) + [math]::Abs($chinaCount - 1441) + [math]::Abs($turkiyeCount - 180)

$nonNACellProblems = 0
foreach ($col in @('Blank_EA','Blank_IEA','Blank_MEA','Blank_DEA','Invalid_EA','Invalid_IEA','Invalid_MEA','Invalid_DEA','NonFinite_EA','NonFinite_IEA','NonFinite_MEA','NonFinite_DEA')) {
    $nonNACellProblems += Sum-Column $fileAudit $col
}
$criticalFileProblems = $wrongRows + $badHeaders + $badHeaderSyntax + $malformedRows + $duplicateIDRows + $blankIDs + $unknownIDs + $missingExpectedIDs + $readErrors + $countryCountIssues + $filenameIssues + $coverageGaps
$technicalStatus = if ($criticalFileProblems -eq 0 -and $nonNACellProblems -eq 0 -and $mappingReferenceProblems -eq 0 -and $fileAudit.Count -eq 5372) { 'PASS: no structural, ID, coverage or non-NA numeric anomalies were detected by this audit.' } else { 'REVIEW REQUIRED: one or more checks found anomalies. See Issues, Mapping_Audit, File_Audit and Coverage_Audit reports.' }

$summary = [System.Collections.Generic.List[string]]::new()
$summary.Add('UHII DATASET FINAL AUDIT')
$summary.Add('Generated: ' + (Get-Date -Format 'yyyy-MM-dd HH:mm:ss'))
$summary.Add('Source folder: ' + $datasetDir)
$summary.Add('Reports folder: ' + $outputDir)
$summary.Add('')
$summary.Add('OVERALL TECHNICAL STATUS')
$summary.Add($technicalStatus)
$summary.Add('This is a technical data-quality audit, not proof of scientific validity or causal interpretation.')
$summary.Add('')
$summary.Add('REFERENCE / MAPPING')
$summary.Add("CityInfo.csv rows=$($cityRows.Count); unique IDs=$($cityIds.Count); blank IDs=$cityBlankIds; duplicate ID rows=$cityDuplicateRows.")
$summary.Add("CityInfo_with_Country.csv rows=$($mappingRows.Count); unique IDs=$($expectedIds.Count); blank IDs=$mappingBlankIds; duplicate ID rows=$mappingDuplicateRows.")
$summary.Add("IDs only in mapping=$idsOnlyInMapping; IDs only in CityInfo=$idsOnlyInCityInfo; coordinate/area mismatch cells=$coordinateMismatchCells (compared=$coordinateCompared; comparison available=$coordinateCompareAvailable).")
$summary.Add("Country labels: China=$chinaCount; Türkiye=$turkiyeCount; blank=$blankCountryCount; other countries=$otherCountryCount.")
$summary.Add('')
$summary.Add('FILES / STRUCTURE')
$summary.Add("CSV files found=$($fileAudit.Count); expected=5372.")
$summary.Add("Wrong row-count files=$wrongRows; required-column problem files=$badHeaders; malformed header/empty-file issues=$badHeaderSyntax; malformed rows=$malformedRows; read errors=$readErrors.")
$summary.Add("Duplicate ID rows=$duplicateIDRows; blank IDs=$blankIDs; distinct unknown IDs summed across files=$unknownIDs; missing expected IDs summed across files=$missingExpectedIDs.")
$summary.Add("Country-count mismatch issue records=$countryCountIssues; filename/combination issues=$filenameIssues; incomplete indicator-year-period coverage groups=$coverageGaps.")
$summary.Add('')
$summary.Add('MEASUREMENT CELLS')
$summary.Add("Non-NA blank + other-invalid + non-finite cells=$nonNACellProblems. NA is reported separately and is not converted to zero.")
foreach ($col in @('Intensity_EA','Intensity_IEA','Intensity_MEA','Intensity_DEA')) {
    $na = 0L; $blank = 0L; $invalid = 0L; $nonfinite = 0L; $valid = 0L
    $short = $col -replace '^Intensity_',''
    $na = Sum-Column $fileAudit ('NA_' + $short)
    $blank = Sum-Column $fileAudit ('Blank_' + $short)
    $invalid = Sum-Column $fileAudit ('Invalid_' + $short)
    $nonfinite = Sum-Column $fileAudit ('NonFinite_' + $short)
    $valid = Sum-Column $fileAudit ('Valid_' + $short)
    $summary.Add("$col`: valid numeric=$valid; NA=$na; blank=$blank; other non-numeric=$invalid; non-finite=$nonfinite.")
}
$summary.Add('')
$summary.Add('COUNTRY-SPECIFIC NA COUNTS')
foreach ($country in @('China','Türkiye')) {
    $rows = @($countryAudit | Where-Object { $_.Country -eq $country })
    $na = Sum-Column $rows 'NA_Count'; $cells = Sum-Column $rows 'CellsChecked'
    $rate = if ($cells -gt 0) { [math]::Round(100.0 * $na / $cells, 6) } else { 0 }
    $filesWithNA = Count-Where $rows { [long]$_.NA_Count -gt 0 }
    $summary.Add("$country`: NA=$na / $cells checked cells; rate=$rate%; files with at least one NA=$filesWithNA.")
}
$summary.Add('')
$summary.Add('COVERAGE CONFIGURATION')
$summary.Add('The audit checks monthly codes 1-12, seasonal codes 21-24 and annual code 30 for Day/Nig files.')
$summary.Add('Configured year ranges: Mod1/Mod2 2001-2021; AMod2/SAT/SMod2 2001-2020; Myd1/Myd2 2003-2021; SMyd1 2003-2020.')
$summary.Add("Coverage groups not complete=$coverageGaps. These configured ranges are based on the existing project scan; verify them against source documentation before publication.")
$summary.Add('')
$summary.Add('SCIENTIFIC LIMITATIONS / NEXT DECISIONS')
$summary.Add('1. NA counts do not explain why observations are missing. Do not replace NA with zero without source-based justification.')
$summary.Add('2. Value ranges are descriptive across overlapping monthly, seasonal and annual files; they are not independent observations.')
$summary.Add('3. Country mapping and the 1,441/180 sample define the current main sample only. Keep the 83 previously noted unlabeled records and any boundary cases outside the main comparison unless independently resolved.')
$summary.Add('4. After reviewing any flagged issues, lock common indicator/year/method combinations and document the selection rules before ML; prevent target leakage and use spatially defensible validation.')
$summary.Add('')
$summary.Add('OUTPUT FILES')
$summary.Add('UHII_Final_Mapping_Audit.csv')
$summary.Add('UHII_Final_File_Audit.csv')
$summary.Add('UHII_Final_Country_NA_Audit.csv')
$summary.Add('UHII_Final_Coverage_Audit.csv')
$summary.Add('UHII_Final_Audit_Issues.csv')
$summary.Add('UHII_Final_Value_Ranges.csv')
$summary.Add('UHII_Final_Audit_Summary.txt')
$summary | Set-Content -LiteralPath $summaryPath -Encoding UTF8

Write-Host '[4/4] Finished.' -ForegroundColor Green
Write-Host "Files scanned: $($fileAudit.Count)"
Write-Host "Non-NA numeric anomalies: $nonNACellProblems"
Write-Host "Coverage groups to review: $coverageGaps"
Write-Host "Status: $technicalStatus"
Write-Host "Reports saved to: $outputDir" -ForegroundColor Green
Write-Host "Open this first: $summaryPath" -ForegroundColor Yellow
