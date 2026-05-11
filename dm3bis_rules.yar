import "pe"
import "hash"

rule DM3BIS_Exact_Sample_SHA256
{
    meta:
        author = "Incident Response"
        description = "Exact detection for the known dm3bis.exe sample"
        tlp = "clear"
        date = "2026-05-11"
        sha256 = "b930e707f2fe248779795723d6246574179eda13cf466967bff1289921b6bfb2"

    condition:
        uint16(0) == 0x5A4D and
        hash.sha256(0, filesize) == "b930e707f2fe248779795723d6246574179eda13cf466967bff1289921b6bfb2"
}

rule DM3BIS_Family_Behavioral
{
    meta:
        author = "Incident Response"
        description = "Behavioral detection for dm3bis ransomware family"
        confidence = "high"
        date = "2026-05-11"

    strings:
        $s1 = "la srs c'est vraiment super !!!!" ascii
        $s2 = "SOFTWARE\\Microsoft\\Windows\\CurrentVersion\\Run" wide ascii
        $s3 = "SuperProgram" wide ascii
        $s4 = "2y6268x13ic4o8b0y4rinj4kz.canarytokens.com" ascii wide
        $s5 = "zoglu.de" ascii wide
        $s6 = "Calculator.exe" ascii wide
        $s7 = "ProcessHacker.exe" ascii wide
        $s8 = "Wireshark.exe" ascii wide
        $s9 = "Ida64.exe" ascii wide

    condition:
        uint16(0) == 0x5A4D and
        pe.machine == pe.MACHINE_AMD64 and
        pe.imports("bcrypt.dll", "BCryptEncrypt") and
        pe.imports("bcrypt.dll", "BCryptGenerateSymmetricKey") and
        pe.imports("DNSAPI.dll", "DnsQuery_W") and
        pe.imports("ADVAPI32.dll", "RegSetValueExW") and
        5 of ($s*)
}

rule DM3BIS_Crypto_Profile
{
    meta:
        author = "Incident Response"
        description = "Crypto configuration profile used by dm3bis (AES-CBC with CNG)"
        confidence = "medium"
        date = "2026-05-11"

    strings:
        $c1 = "AES" wide ascii
        $c2 = "BlockLength" wide ascii
        $c3 = "ChainingMode" wide ascii
        $c4 = "ChainingModeCBC" wide ascii
        $c5 = "la srs c'est vraiment super !!!!" ascii

    condition:
        uint16(0) == 0x5A4D and
        pe.imports("bcrypt.dll", "BCryptOpenAlgorithmProvider") and
        pe.imports("bcrypt.dll", "BCryptSetProperty") and
        pe.imports("bcrypt.dll", "BCryptEncrypt") and
        4 of ($c*)
}
