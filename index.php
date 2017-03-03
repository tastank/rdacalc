<?php
// Morey Airport, Middleton, WI
$lat = 43.113381;
$lon = -89.528386;
// The approximate service ceiling of a fully loaded C172E
$da = 14000;
if (isset($_POST["da"]) && isset($_POST["lat"]) && isset($_POST["lon"])) {
    $lat = $_POST["lat"];
    $lon = $_POST["lon"];
    $da = $_POST["da"];
    $rap_file = shell_exec("python update_rap.py -v");
    $python_cmd = escapeshellcmd("python rdacalc.py --grib-file " . $rap_file . " 14000 43.113381 -89.528386");
    $ceiling = shell_exec($python_cmd);
}
?>
<html>
<head>
<title>Effective Service Ceiling Calculator</title>
</head>
<body>
Note: this calculator only works with latitudes and longitudes within the contiguous United States and some nearby regions.
<form method="POST">
<table>
<tr>
<td>Density altitude:</td><td><input type="text" name="da" value="<?php echo $da; ?>" /></td>
</tr><tr>
<td>Latitude:</td><td><input type="text" name="lat" value="<?php echo $lat; ?>" /></td>
</tr><tr>
<td>Longitude:</td><td><input type="text" name="lon" value="<?php echo $lon; ?>" /></td>
</tr><tr>
<td><input type="submit" name="submit" value="Calculate MSL altitude" /></td><td><?php if (isset($ceiling)) {echo $ceiling;} ?></td>
</tr>
</table>
</form>
</body>
</html>
