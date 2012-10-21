<?php
// Mycode Plugin to get a sensible [code]... sheesh
// By Arkady Sadik http://www.arkady-sadik.de/
// Version 1.0

$plugins->add_hook("parse_message", "precode_run");

function precode_info()
{
    return array(
        "name"        => "PreCode BBCode",
        "description" => "Sensible Code BBCode",
        "website"     => "http://www.arkady-sadik.de/",
        "author"      => "Arkady Sadik",
        "authorsite"  => "http://www.arkady-sadik.de/",
        "version"     => "1.0",
	);
}

function precode_activate()
{
}

function precode_deactivate()
{
}

function precode_run($message)
{
    // preg_replace_callback errors out when stuff is too big. Wuzzy.
    $str = "";
    $pos = 0;
    while ($pos < strlen($message)) {
        $convo_start = strpos($message, "[pre]", $pos);
        if ($convo_start === false) {
            $str .= substr($message, $pos);
            return $str;
        }
        $convo_end = strpos($message, "[/pre]", $convo_start+5);
        if ($convo_end === false) {
            $str .= substr($message, $pos);
            return $str;
        }
        $str .= substr($message, $pos, ($convo_start-$pos));
        $str .= "<pre>"
        $str .= substr($message, $convo_start+5, ($convo_end-($convo_start+5)));
        $str .= "</pre>"
        $pos = $convo_end + 8;
    }
    return $str;
}

?>
