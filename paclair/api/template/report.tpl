<html>
<head>
    <META http-equiv="Content-Type" content="text/html">
    <style>
        body {
            background: white;
            color: black;
            margin: 10px;
            font-family: Verdana, Arial, Helvetica, sans-serif;
            font-size: 10pt;
        }
    
        thead td {
            color: #999;
            font-size: 90%;
            text-transform: uppercase;
            font-weight: 300;
            padding-top: 0 !important;
            padding-left: 10px;
        }
    
        html {
            font-family: sans-serif;
            -webkit-text-size-adjust: 100%;
            -ms-text-size-adjust: 100%
        }
    
        h3 {
            text-transform: uppercase;
            color: rgb(214, 68, 86);
        }
    
        .arrow-right {
            background: url('data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAABAAAAAQCAYAAAAf8/9hAAAABmJLR0QA/wD/AP+gvaeTAAAAT0lEQVQ4jWNgGLagjIGBoYISAzoZGBj+U2pII9SQBkoMaaK5IUxEGPAXSnOQY3sPPtsJgT5KNLdDNXcSUsiMQ9yGgYHhFAMDQzk5tg8xAAAvBBGfk/o9QQAAAABJRU5ErkJggg==') no-repeat top left;
            padding-left: 20px;
        }
    
        .arrow-bottom {
            background: url('data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAABAAAAAQCAYAAAAf8/9hAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsMAAA7DAcdvqGQAAAAGYktHRAD/AP8A/6C9p5MAAABWSURBVDhPYxgF1Af1QNwOYWIFnUBcBmFiByAF/4G4D8xDBY1ADJKrAPPwAJghPWAeBDQBMVGaYaABiEEaQF6CaQaJkQRghpClGQY6gJhszaOAKMDAAADTkRImC1I08QAAAABJRU5ErkJggg==') no-repeat top left;
            padding-left: 20px;
        }
    
        .title {
            font-size: 16pt;
            border-bottom:  1px solid #000000;
            font-weight: bold;
            padding:20 20 20 0;
        }

        .subtitle {
            color: #999;
            font-size: 90%;
            text-transform: uppercase;
            font-weight: 300;
            padding-top: 0 !important;
            text-align: left;
            margin-bottom: 6px;
        }
    
        table {
            width: 100%;
        }
    
        A {
            text-decoration: none;
            color: #333333;
            word-break: break-all;
        }
    
        tbody#vulnerabilities td {
            border-bottom: 1px solid #eee;
            padding: 10px;
            cursor: pointer;
        }
    
    
        label {
            display: inline-block;
            max-width: 100%;
            margin-bottom: 5px;
            font-weight: 700;
        }
    
        dl {
            display: inline-block;
            vertical-align: top;
            max-width: 200px;
            padding-right: 20px;
        }
    
        dt {
            margin-bottom: 10px;
            cursor: default;
        }
    
        dd {
            cursor: default;
            margin-left: 0;
            color: lightgray;
        }
    
    
        span .title {
            float: right;
            min-width: 300px;
            margin-bottom: 10px;
        }
    
        .hidden {
            display: none;
        }
    
        .Medium {
            color: rgb(252, 166, 87);
        }
    
        .Low {
            color: rgb(248, 202, 28);
        }
    
        .Negligible {
            color: rgb(155, 155, 155);
        }
    
        .Critical,
        .cvss_crit {
            color: rgb(214, 68, 86);
        }
    
        .High,
        .cvss_high {
            color: rgb(247, 116, 84);
        }
    
        .fixed,
        .cvss_low {
            color: #2fc98e;
        }
    
        .fixable {
            float: right;
            margin-bottom: 10px;
        }
    
        [tooltip]:before {
            /* needed - do not touch */
            content: attr(tooltip);
            position: absolute;
            opacity: 0;
    
            /* customizable */
            transition: all 0.15s ease;
            padding: 10px;
            color: white;
            border-radius: 10px;
            box-shadow: 2px 2px 1px silver;
            width: 300px;
            font-size: 13px;
        }
    
        [tooltip]:hover:before {
            /* needed - do not touch */
            opacity: 1;
    
            /* customizable */
            background: black;
            margin-top: -50px;
            margin-left: 20px;
        }
    
        [tooltip]:not([tooltip-persistent]):before {
            pointer-events: none;
        }
    </style>
    <script>
        
        var cvss = {"Access Vector" : "This metric reflects how the vulnerability is exploited. The more remote an attacker can be to attack a host, the greater the vulnerability score.",
                    "Access Complexity" : "This metric measures the complexity of the attack required to exploit the vulnerability once an attacker has gained access to the target system. For example, consider a buffer overflow in an Internet service: once the target system is located, the attacker can launch an exploit at will.",
                    "Authentication" : "This metric measures the number of times an attacker must authenticate to a target in order to exploit a vulnerability. This metric does not gauge the strength or complexity of the authentication process, only that an attacker is required to provide credentials before an exploit may occur.&nbsp;  The fewer authentication instances that are required, the higher the vulnerability score.",
                    "Confidentiality Impact" : "This metric measures the impact on confidentiality of a successfully exploited vulnerability. Confidentiality refers to limiting information access and disclosure to only authorized users, as well as preventing access by, or disclosure to, unauthorized ones. Increased confidentiality impact increases the vulnerability score.",
                    "Integrity Impact" : "This metric measures the impact to integrity of a successfully exploited vulnerability. Integrity refers to the trustworthiness and guaranteed veracity of information. Increased integrity impact increases the vulnerability score.",
                    "Availability Impact" : "This metric measures the impact to availability of a successfully exploited vulnerability. Availability refers to the accessibility of information resources. Increased availability impact increases the vulnerability score." };

        var av = {"Network": "A vulnerability exploitable with network access means the vulnerable software is bound to the network stack and the attacker does not require local network access or local access.  Such a vulnerability is often termed \"remotely exploitable\".  An example of a network attack is an RPC buffer overflow.",
                  "Adjacent Network" : "A vulnerability exploitable with adjacent network access requires the attacker to have access to either the broadcast or collision domain of the vulnerable software.  Examples of local networks include local IP subnet, Bluetooth, IEEE 802.11, and local Ethernet segment.",
                  "Local": "A vulnerability exploitable with only local access requires the attacker to have either physical access to the vulnerable system or a local (shell) account. Examples of locally exploitable vulnerabilities are peripheral attacks such as Firewire/USB DMA attacks, and local privilege escalations (e.g., sudo)."},
            ac = {"Low" : "Specialized access conditions or extenuating circumstances do not exist making this easy to exploit",
                  "Medium" : "The access conditions are somewhat specialized making this somewhat difficult to exploit",
                  "High" : "Specialized access conditions exist making this harder to exploit" },
            au = {"None" : "Authentication is not required to exploit the vulnerability.",
                  "Single" : "The vulnerability requires an attacker to be logged into the system (such as at a command line or via a desktop session or web interface).",
                  "Multiple" : "Exploiting the vulnerability requires that the attacker authenticate two or more times, even if the same credentials are used each time. An example is an attacker authenticating to an operating system in addition to providing credentials to access an application hosted on that system."},
            C = {"Complete" : "There is total information disclosure, resulting in all system files being revealed. The attacker is able to read all of the system's data (memory, files, etc.)",
                 "Partial" : "There is considerable informational disclosure. Access to some system files is possible, but the attacker does not have control over what is obtained, or the scope of the loss is constrained. An example is a vulnerability that divulges only certain tables in a database.",
                 "None" : "There is no impact to the confidentiality of the system."},
            I = {"Complete" : "There is a total compromise of system integrity. There is a complete loss of system protection, resulting in the entire system being compromised. The attacker is able to modify any files on the target system",
                 "Partial" : "Modification of some system files or information is possible, but the attacker does not have control over what can be modified, or the scope of what the attacker can affect is limited. For example, system or application files may be overwritten or modified, but either the attacker has no control over which files are affected or the attacker can modify files within only a limited context or scope.",
                 "None" : "There is no impact to the integrity of the system."},
            A = {"Complete" : "There is a total shutdown of the affected resource. The attacker can render the resource completely unavailable.",
                 "Partial" : "There is reduced performance or interruptions in resource availability. An example is a network-based flood attack that permits a limited number of successful connections to an Internet service.",
                 "None" : "There is no impact to the availability of the system."};
                  

        function filter() {
            var x = document.getElementById('filter'),
                y = document.getElementsByClassName('fixed'),
                rows = document.getElementById("vulnerabilities").rows,
                display = "";
            if (x.checked === true) {
                for (i = 0; i < rows.length; i += 2) {
                    display = (rows[i].children[4].children[0].className !== "fixed") ? "none" : "";
                    rows[i].style.display = display;
                    rows[i + 1].style.display = display;
                }
            } else {
                for (i = 0; i < rows.length; i += 2) {
                    rows[i].style.display = display;
                    rows[i + 1].style.display = display;
                }
            }
            compute();
        }

        function showtooltip(obj, name) {
            obj.attributes.tooltip.value = (name === undefined) ? '' : name;
        }

        function switcher(id) {
            var x = document.getElementById("desc_" + id);
            x.className = (x.className === "hidden") ? "" : "hidden";
            x.style.cursor = "default";
            x.parentNode.previousElementSibling.children[0].children[0].className = (x.className === "hidden") ? "arrow-right" : "arrow-bottom";
        }

        function compute() {
            var t = { "Critical": 0, "High": 0, "Medium": 0, "Low": 0, "Negligible": 0 },
                rows = document.getElementById("vulnerabilities").rows,
                name = "",
                total = 0;
            for (i = 0; i < rows.length; i += 2) {
                if (rows[i].style.display != "none") {
                    name = rows[i].children[1].children[0].className;
                    t[name]++
                    total++;
                }
            }

            var res = 0, i = 0;
            for (var sev in t) {
                res = (total === 0) ? 0 : 200 * (t[sev] / total);
                document.getElementById(sev).style.height = Math.ceil(res);
                document.getElementById(sev).attributes.tooltip.value = sev + ": " + t[sev] + " (" + Math.round(res / 2) + "%" + ")";
                document.getElementById("risk").rows[0].children[i++].firstChild.nodeValue = t[sev];
            }
        }

    </script>

</head>

<body onload="javascript:compute();">
    <div class='title'>
        <b>PAClair Security Reporting</b>
    </div>
    <h3>Number of Vulnerabilities by Risk</h3>
    <table id="risk" style="height: 200; width:80%;">
        <tbody>
            <tr>
                <td valign="bottom" align="center" width="20%">0
                        <br>
                        <div id="Critical" tooltip="Critical: 0" style="height:0; width:100%; background-color:rgb(214, 68, 86);"></div>
                        Critical
                </td>
                <td valign="bottom" align="center" width="20%">0
                        <br>
                        <div id="High" tooltip="High: 0" style="height:0; width:100%; background-color: rgb(247, 116, 84);"></div>
                        High
                </td>
                <td valign="bottom" align="center" width="20%">0
                        <br>
                        <div id="Medium" tooltip="Medium: 0" style="height:0; width:100%; background-color:rgb(252, 166, 87);"></div>
                        Medium
                </td>                                                                       
                <td valign="bottom" align="center" width="20%">0
                        <br>
                        <div id="Low" tooltip="Low: 0" style="height:0; width:100%; background-color:rgb(248, 202, 28);"></div>
                        Low
                </td>
                <td valign="bottom" align="center" width="20%">0
                        <br>
                        <div id="Negligible" tooltip="Negligible: 0" style="height:0; width:100%; background-color:rgb(155, 155, 155);"></div>
                        Negligible
                </td>               
            </tr>
        </tbody>
    </table>
    <br/>
    <span class='fixable'>
        <label>
            <input id="filter" autocomplete="off" type="checkbox" onclick="filter()" /> Only show fixable
        </label>
    </span>
    <h3>Asset Vulnerabilities</h3>
    <table>
        <thead>
            <td>cve</td>
            <td>severity</td>
            <td>package</td>
            <td>current version</td>
            <td>fixed in version</td>
            <td>introduced in</td>
        </thead>
        % count = 0 
        <tbody id="vulnerabilities">
        % for line in info:
            <tr onclick="javascript:switcher('{{count}}');">
                <td><div class='arrow-right'>{{line["CVE"]}}</div></td>
                <td>
                    <div class='{{line["SEVERITY"]}}'> {{line["SEVERITY"]}}
                        <div>
                </td>
                <td>{{line["PACKAGE"]}}</td>
                <td>{{line["CURRENT"]}}</td>
                <td>
                    <div {{ ! 'class=fixed' if line[ "FIXED"] !="" else "" }}>{{line["FIXED"]}}</div>
                </td>
                <td>{{line["INTRODUCED"]}}</td>
            </tr>
            <tr>
                <td colspan=6 id='desc_{{count}}' class="hidden">
                    <div>
                        <div class="subtitle">Description:</div>
                        <p>{{line["DESCRIPTION"]}}</p>
                        <div class="subtitle">Technical Impact:</div>

                        <div>
                            <dl>
                                <dt tooltip="" onmouseover="javascript:showtooltip(this, cvss['Access Vector']);">Access Vector</dt>
                                <dd tooltip="" onmouseover="javascript:showtooltip(this, av['Network']);">
                                    {{!"<b class='cvss_crit'>Network</b>" if line["VECTORS"]["Access Vector"] == "Network" else "Network" }}
                                </dd>
                                <dd tooltip="" onmouseover="javascript:showtooltip(this, av['Adjacent Network']);">
                                    {{!"<b class='cvss_high'>Adjacent Network</b>" if line["VECTORS"]["Access Vector"] == "Adjacent Network" else "Adjacent Network" }}
                                </dd>
                                <dd tooltip="" onmouseover="javascript:showtooltip(this, av['Local']);">
                                    {{!"<b class='cvss_low'>Local</b>" if line["VECTORS"]["Access Vector"] == "Local" else "Local" }}
                                </dd>
                            </dl>
                            <dl>
                                <dt tooltip="" onmouseover="javascript:showtooltip(this, cvss['Access Complexity']);">Access Complexity</dt>
                                <dd tooltip="" onmouseover="javascript:showtooltip(this, ac['Low']);">
                                    {{!"<b class='cvss_crit'>Low</b>" if line["VECTORS"]["Access Complexity"] == "Low" else "Low" }}
                                </dd>
                                <dd tooltip="" onmouseover="javascript:showtooltip(this, ac['Medium']);">
                                    {{!"<b class='cvss_high'>Medium</b>" if line["VECTORS"]["Access Complexity"] == "Medium" else "Medium" }}
                                </dd>
                                <dd tooltip="" onmouseover="javascript:showtooltip(this, ac['High']);">
                                    {{!"<b class='cvss_low'>High</b>" if line["VECTORS"]["Access Complexity"] == "High" else "High" }}
                                </dd>
                            </dl>
                            <dl>
                                <dt tooltip="" onmouseover="javascript:showtooltip(this, cvss['Authentication']);">Authentication</dt>
                                <dd tooltip="" onmouseover="javascript:showtooltip(this, au['None']);">
                                    {{!"<b class='cvss_crit'>None</b>" if line["VECTORS"]["Authentication"] == "None" else "None" }}
                                </dd>
                                <dd tooltip="" onmouseover="javascript:showtooltip(this, au['Single']);">
                                    {{!"<b class='cvss_high'>Single</b>" if line["VECTORS"]["Authentication"] == "Single" else "Single" }}
                                </dd>
                                <dd tooltip="" onmouseover="javascript:showtooltip(this, au['Multiple']);">
                                    {{!"<b class='cvss_low'>Multiple</b>" if line["VECTORS"]["Authentication"] == "Multiple" else "Multiple" }}
                                </dd>
                            </dl>
                            <dl>
                                <dt tooltip="" onmouseover="javascript:showtooltip(this, cvss['Confidentiality Impact']);">Confidentiality Impact</dt>
                                <dd tooltip="" onmouseover="javascript:showtooltip(this, C['Complete']);">
                                    {{!"<b class='cvss_crit'>Complete</b>" if line["VECTORS"]["Confidentiality impact"] == "Complete" else "Complete" }}
                                </dd>
                                <dd tooltip="" onmouseover="javascript:showtooltip(this, C['Partial']);">
                                    {{!"<b class='cvss_high'>Partial</b>" if line["VECTORS"]["Confidentiality impact"] == "Partial" else "Partial" }}
                                </dd>
                                <dd tooltip="" onmouseover="javascript:showtooltip(this, C['None']);">
                                    {{!"<b class='cvss_low'>None</b>" if line["VECTORS"]["Confidentiality impact"] == "None" else "None" }}
                                </dd>
                            </dl>
                            <dl>
                                <dt tooltip="" onmouseover="javascript:showtooltip(this, cvss['Integrity Impact']);">Integrity Impact</dt>
                                <dd tooltip="" onmouseover="javascript:showtooltip(this, I['Complete']);">
                                    {{!"<b class='cvss_crit'>Complete</b>" if line["VECTORS"]["Integrity impact"] == "Complete" else "Complete" }}
                                </dd>
                                <dd tooltip="" onmouseover="javascript:showtooltip(this, I['Partial']);">
                                    {{!"<b class='cvss_high'>Partial</b>" if line["VECTORS"]["Integrity impact"] == "Partial" else "Partial" }}
                                </dd>
                                <dd tooltip="" onmouseover="javascript:showtooltip(this, I['None']);">
                                    {{!"<b class='cvss_low'>None</b>" if line["VECTORS"]["Integrity impact"] == "None" else "None" }}
                                </dd>
                            </dl>
                            <dl>
                                <dt tooltip="" onmouseover="javascript:showtooltip(this, cvss['Availability Impact']);">Availability Impact</dt>
                                <dd tooltip="" onmouseover="javascript:showtooltip(this, A['Complete']);">
                                    {{!"<b class='cvss_crit'>Complete</b>" if line["VECTORS"]["Availability impact"] == "Complete" else "Complete" }}
                                </dd>
                                <dd tooltip="" onmouseover="javascript:showtooltip(this, A['Partial']);">
                                    {{!"<b class='cvss_high'>Partial</b>" if line["VECTORS"]["Availability impact"] == "Partial" else "Partial" }}
                                </dd>
                                <dd tooltip="" onmouseover="javascript:showtooltip(this, A['None']);">
                                    {{!"<b class='cvss_low'>None</b>" if line["VECTORS"]["Availability impact"] == "None" else "None" }}
                                </dd>
                            </dl>                        
                        </div>
                        <div class="subtitle">Additionnal information:</div>
                            <p><a href='{{line["LINK"]}}' target='_blank'>{{line["LINK"]}}</a></p>
                        </p>
                    </div>
                </td>
            </tr>
        % count = count + 1 
    % end
        </tbody>
    </table>
</body>
</html>
