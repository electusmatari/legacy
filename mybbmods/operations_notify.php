<?php
/*
operations_notify.php --- Operations Notify for MyBB
Copyright (c) 2009, 2010, 2011 Arkady Sadik

Author: Arkady Sadik <arkady@arkady-sadik.de>

Idea taken from Calendar Warner by Online Urbanus

This program is free software; you can redistribute it and/or
modify it under the terms of the GNU General Public License
as published by the Free Software Foundation; either version 2
of the License, or (at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program; if not, write to the Free Software
Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA
02110-1301, USA.
*/

if(!defined("IN_MYBB"))
{
    die("This file cannot be accessed directly.");
}

function operations_notify_info()
{
    return array("name"        => "Operations Notify",
                 "description" => "Notifies of ongoing events from an operations forum",
                 "website"     => "none",
                 "author"      => "Arkady Sadik",
                 "authorsite"  => "http://www.arkady-sadik.de/",
                 "version"     => "1.5",
           );
}

$plugins->add_hook("pre_output_page", "operations_notify_run");

function operations_notify_activate()
{
}

function operations_notify_deactivate()
{
}

function operations_notify_run($page)
{
    global $mybb, $db;

    $wanted_fids = array();
    $operation_fids = array(111, 144, 145, 149);
    $fid_suffix = array(144 => ' <span class="grdforum">GRD</span>',
                        145 => ' <span class="grdforum">LUTI</span>',
                        149 => ' <span class="grdforum">Allies</span>');
    foreach ($operation_fids as $fid)
    {
        $fpermissions = forum_permissions($fid);
        if($fpermissions['canview'] == 1)
        {
            $wanted_fids[] = $fid;
        }
    }
    if (count($wanted_fids) == 0)
    {
        return $page;
    }

    opnotify_handle_post();

    $expander_begin_end = opnotify_expander();
    $expander = $expander_begin_end[0];
    $begin = $expander_begin_end[1];
    $end = $expander_begin_end[2];

    $html = ('<table border="0" cellspacing="1" cellpadding="4" class="tborder"><tr><td class="thead">' .
             '<span class="smalltext"><strong><span id="opevt"></span>Upcoming Operations</strong> '.
             $expander);

    $html .= ('<span id="opnotify_announce">'
              . opnotify_announce_form()
              . '</span>');

    $html .= '</span></td></tr>';

    $html .= opnotify_ongoing_operations();
    $html .= opnotify_upcoming_operations($wanted_fids, $fid_suffix,
                                          $begin, $end);

    $page = str_replace("</head>",
                        "<script type=\"text/javascript\">"
                        . opnotify_javascript()
                        . "</script></head>",
                        $page);
    $page = str_replace("<div id=\"content\">",
                        "<div id=\"content\">" . $html,
                        $page);
    return $page;
}

function opnotify_handle_post () {
    global $mybb, $db;

    if ($mybb->input['action'] == 'dooperationsnotify'
        && $mybb->request_method == 'post'
        && trim($mybb->input['description']) != '') {

        $db->insert_query("ongoing_operations", array(
            "uid" => intval($mybb->user["uid"]),
            "description" => $db->escape_string($mybb->input['description'])));

        redirect("index.php");
    }
    if ($mybb->input['action'] == 'dodeloperationsnotify'
        && $mybb->request_method == 'post') {

        $db->query("
UPDATE ".TABLE_PREFIX."ongoing_operations
  SET active = 0
WHERE uid = " . intval($mybb->user["uid"]) . "
  AND id = " . intval($mybb->input['opid']) . "
;");

        redirect("index.php");
    }
}

function opnotify_ongoing_operations () {
    global $mybb, $db;

    $html = "";

    $query = $db->query("
SELECT o.id AS id,
       o.description AS description,
       FLOOR((UNIX_TIMESTAMP(NOW()) - UNIX_TIMESTAMP(o.created))/60) AS age,
       o.uid AS uid,
       u.username AS creator
FROM ".TABLE_PREFIX."ongoing_operations o
     INNER JOIN ".TABLE_PREFIX."users u
       ON o.uid = u.uid
WHERE active
  AND (UNIX_TIMESTAMP(NOW()) - UNIX_TIMESTAMP(o.created)) <= (60*60)
ORDER BY o.created ASC
;");
    while ($op = $db->fetch_array($query))
    {
        $html .= ('<tr><td class="trow1"><small><b>Ongoing: '
                  . $op['description']
                  . ' (' . $op['age'] . ($op['age'] == 1 ? ' minute' : ' minutes')
                  . '  ago by ' . $op['creator'] . ')'
                  . "</b></small>");
        if ($mybb->user['uid'] == $op['uid']) {
            $html .= '<form action="/forums/" method="post" style="display: inline"><input type="hidden" name="action" value="dodeloperationsnotify" /><input type="hidden" name="opid" value="'.$op['id'].'" /><input type="submit" value="delete" style="font-size: xx-small; padding: 0; margin: 0; margin-left: 2em;" /></form>';
        }
        $html .= "</td></tr>";
    }
    return $html;
}

function opnotify_upcoming_operations ($wanted_fids, $fid_suffix,
                                       $begin, $end) {
    global $mybb, $db;

    $html = "";
    $query = $db->query("
SELECT fid, subject, tid, prefix
FROM ".TABLE_PREFIX."threads
WHERE fid IN (" . join(", ", $wanted_fids) . ")
  AND sticky = 0
  AND subject REGEXP '[0-9][0-9][0-9]\\.[0-9][0-9]\\.[0-9][0-9]'
ORDER BY subject ASC
;
");
    while ($thread = $db->fetch_array($query))
    {
        if (preg_match("/^([0-9][0-9][0-9])\\.([0-9][0-9])\\.([0-9][0-9]).(.*)/",
                       $thread['subject'],
                       $matches))
        {
            $timestamp = mktime(0, 0, 0, $matches[2], $matches[3],
                                $matches[1] + 1898);
            if ($timestamp > $begin && $timestamp < $end)
            {
                if ($thread['prefix'] == 9)
                {
                    $style = " style=\"color: #FF0000; font-weight: bold;\"";
		}
                else
                {
                    $style = "";
                }
                if ($mybb->input['opexpand'])
                {
                    $title = ($matches[1] .
                              "." . $matches[2] .
                              "." . $matches[3] .
                              " " . $matches[4]);
                }
                else
                {
                    $title = $matches[4];
                }
                if (array_key_exists($thread["fid"], $fid_suffix))
                {
                    $title .= $fid_suffix[$thread["fid"]];
                }
                $html .= ('<tr><td class="trow1"><small><a href="'
                          . get_thread_link($thread['tid'])
                          . "\"$style>"
                          . $title
                          . "</a></small></td></tr>");
            }
        }
    }
    $html .= "</table><br />";
    return $html;
}

function opnotify_expander () {
    global $mybb, $db;

    $now = time();
    $begin = $now - (24 * 60 * 60);
    $opexpand = $mybb->input['opexpand'];
    if ($opexpand)
    {
        $end = $now + (24 * 60 * 60 * 365);
        $location = get_current_location();
        $location = str_replace('?opexpand=true', '', $location);
        $location = str_replace('&amp;opexpand=true', '', $location);
        $expander = '<a href="'.$location.'">(fold)</a>';
    }
    else
    {
        $end = $now + (2 * 24 * 60 * 60);
        $location = get_current_location();
        $pos = strpos($location, "?");
        if($pos === false)
        {
            $location .= "?opexpand=true";
        }
        elseif ($pos == strlen($location) - 1)
        {
            $location .= "opexpand=true";
        }
        else
        {
            $location .= "&amp;opexpand=true";
        }
        $expander = '<a href="'.$location.'">(expand)</a>';
    }

    return array($expander, $begin, $end);
}

function opnotify_javascript () {
    $js = "
function getevt() {
    d = new Date();
    weekday = ['Sun','Mon','Tue','Wed','Thu','Fri','Sat'][d.getUTCDay()];
    hour = d.getUTCHours();
    if (hour < 10) {
        hour = '0' + hour;
    }
    minute = d.getUTCMinutes();
    if (minute < 10) {
        minute = '0' + minute;
    }
    return weekday + ' | ' + hour + ':' + minute + ' | ';
}
function regularevt() {
    elt = document.getElementById('opevt');
    elt.innerHTML = getevt();
    setTimeout('regularevt()', 5000);
}

function opnotify_init() {
    regularevt();
    opnotify_hide();
}

function opnotify_hide() {
    elt = document.getElementById('opnotify_announce');
    elt.innerHTML = '" . opnotify_announce_hidden() . "';
}

function opnotify_show() {
    elt = document.getElementById('opnotify_announce');
    elt.innerHTML = '" . opnotify_announce_form() . "';
}

document.observe('dom:loaded', opnotify_init);
";
    return $js;
}

function opnotify_announce_form () {
    return ('<form action="/forums/" method="post" style="display: inline; float: right"><input type="hidden" name="action" value="dooperationsnotify" /><input type="submit" value="Announce:" style="font-size: x-small; font-weight: bold; border: 0; margin: 0; padding: 0 0.5em; background-color: transparent; color: #FFFFFF" /><input type="text" name="description" style="font-size: xx-small" size="40"/></form>');
}

function opnotify_announce_hidden () {
    return ('<button type="button" onClick="opnotify_show()" style="display: inline; float: right; font-size: x-small; font-weight: bold; border: 0; margin: 0; padding: 0 0.5em; background-color: transparent; color: #FFFFFF">&lt;&lt; Announce</input>');
}
