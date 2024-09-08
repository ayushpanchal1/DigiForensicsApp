rule SuspiciousFile
{
    meta:
        description = "Detects suspicious files"
    strings:
        $a = "suspicious_string"  // Example string pattern to match
    condition:
        $a
}
