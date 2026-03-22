param (
    [int]$matNum = 1 
)

$fail = 0

# __SECTION__ ip test 
$ipRange = $matNum + 10
$targetIp = "192.168.2.$ipRange"
Write-Output "Testing if own IP addr = $targetIp"
$result = Get-NetIPAddress -AddressFamily IPv4 -IPAddress $targetIp -ErrorAction SilentlyContinue
if ($result) {
    Write-Output "SUCCES -- own IP correct"
} else {
    Write-Output "FAIL -- own IP incorrect"
    $fail = $fail + 1
}
Write-Output ""

# __SECTION__ uplink test 
Write-Output "Testing connection to server:"
$result = Test-Connection -ComputerName 192.168.2.1 -Count 5
$received = $result.Count
$avg = ($result | Measure-Object -Property ResponseTime -Average).Average
if ($received -lt 5) {
    Write-Output "FAIL -- server uplink not consistent ($recieved/5)"
    $fail = $fail + 1
} else {
    Write-Output "SUCCES -- server uplink"
    Write-Output "avg delay: $avg ms"
}
Write-Output ""

$success = 2-$fail
Write-Output "TEST DONE"
Write-Output "$success/2 successfull"
Write-Output ""