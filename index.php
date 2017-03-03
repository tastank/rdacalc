<?php
// Morey Airport, Middleton, WI
$lat = 43.113381;
$lon = -89.528386;
// The approximate service ceiling of a fully loaded C172E
$da = 14000;
if (isset($_POST["da"]) && isset($_POST["lat"]) && isset($_POST["lon"])) {
    if (isset($_POST["unit"])) {
        $unit = $_POST["unit"];
        if ($_POST["unit"] == "m") {
            $unit_arg = "-m";
        } else if ($_POST["unit"] == "km") {
            $unit_arg = "--km";
        }
    }
    $lat = $_POST["lat"];
    $lon = $_POST["lon"];
    $da = $_POST["da"];
    $rap_file = shell_exec("python update_rap.py -v");
    $python_cmd = "python rdacalc.py --grib-file " . $rap_file . " " . $da . " " . $lat . " " . $lon;
    if (isset($unit_arg)) {
        $python_cmd .= " " . $unit_arg;
    }
    $ceiling = shell_exec(escapeshellcmd($python_cmd));
}
?>
<html>
<head>
<title>Effective Service Ceiling Calculator</title>
</head>
<body>
Note: this calculator only works with latitudes and longitudes within the contiguous United States and some nearby regions.<br />
<a href="http://www.nco.ncep.noaa.gov/pmb/docs/on388/tableb.html#GRID130">Technical specification of coverage area</a> <a href="http://www.nco.ncep.noaa.gov/pmb/docs/on388/grids/grid130.gif">Graphical depiction of coverage area</a>
<form method="POST">
<table>
<tr>
  <td>Density altitude:</td><td><input type="text" name="da" value="<?php echo $da; ?>" /></td>
</tr><tr>
  <td>Latitude:</td><td><input type="text" name="lat" value="<?php echo $lat; ?>" /></td>
</tr><tr>
  <td>Longitude:</td><td><input type="text" name="lon" value="<?php echo $lon; ?>" /></td>
</tr><tr>
  <td>Altitude unit:</td>
  <td>
    <select name="unit">
      <option value="ft">ft</option>
      <option value="m" <?php if ($unit == "m") echo "selected='selected'"?>>m</option>
      <option value="km" <?php if ($unit == "km") echo "selected='selected'"?>>km</option>
    </select>
  </td>
</tr><tr>
<td><input type="submit" name="submit" value="Calculate MSL altitude" /></td><td><?php if (isset($ceiling)) {echo $ceiling;} ?></td>
</tr>
</table>
</form>
</body>
</html>
