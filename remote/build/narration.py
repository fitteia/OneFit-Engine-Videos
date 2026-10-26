NAME = "ofe-gui-remote-hosts"
TITLE = "OFE-GUI on remote hosts"
IMAGES = {
    "title": "slides/title.png", "why": "slides/why.png", "ssh1": "slides/ssh1.png", "ssh2": "slides/ssh2.png",
    "connect1": "slides/connect1.png", "manual": "slides/manual.png", "reverse": "slides/reverse.png",
    "engine": "slides/engine.png", "choose": "slides/choose.png", "close": "slides/close.png",
    "ssh": "shots/20-ssh.png", "connect": "shots/30-connect.png",
}

# Each sentence: caption text, spoken text (pronunciation fixes), optional
# length_scale, and the shot: image, camera (x, y, width in source px; height
# follows 16:9) and an optional highlight: a box (x0, y0, x1, y1), a list of
# boxes, or slide element names ("slide:name") from slides/boxes.json.
FULL = (0, 0, 3840)
GUI_ALL = (55, 62, 3730)

SECTIONS = [
  {"title": "OFE-GUI on remote hosts", "label": None, "sentences": [
    ("OFE-GUI can run your fits on another computer: a workstation, a lab server, or a virtual machine.",
     "O F E GUI can run your fits on another computer: a workstation, a lab server, or a virtual machine.", None, "title", FULL, None),
    ("Your browser stays on your computer, and the fitting happens over there.",
     None, None, "title", (120, 70, 3600), None),
    ("This tour starts with the -ssh option, and then shows the alternatives.",
     "This tour starts with the dash S S H option, and then shows the alternatives.", None, "title", (200, 120, 3440), None),
  ]},
  {"title": "Where OFE-GUI runs", "label": None, "sentences": [
    ("On its own, OFE-GUI runs on your computer and opens in your browser, at 127.0.0.1, port 8143.",
     "On its own, O F E GUI runs on your computer, and opens in your browser, at one two seven, zero, zero, one; port eighty-one forty-three.", None, "why", FULL, "why:gui"),
    ("It has no login, and it can browse files and run fits, so it never listens on the network.",
     None, None, "why", FULL, "why:why"),
    ("To reach another computer, it uses SSH: your account, your keys and your settings.",
     "To reach another computer, it uses S S H: your account, your keys, and your settings.", None, "why", FULL, "why:ssh"),
  ]},
  {"title": "-ssh", "label": None, "sentences": [
    ("With -ssh, one command starts OFE-GUI on the remote account and connects your browser to it.",
     "With dash S S H, one command starts O F E GUI on the remote account, and connects your browser to it.", None, "ssh1", FULL, "ssh1:target"),
    ("Name the remote programs, and the OFE_PATH their engine needs.",
     "Name the remote programs, and the O F E path their engine needs.", None, "ssh1", FULL, "ssh1:progs"),
    ("-remote-dir picks the folder it starts in, and -enable-terminal adds the Terminal.",
     "Dash remote dir picks the folder it starts in, and dash enable terminal adds the Terminal.", None, "ssh1", FULL, "ssh1:dir"),
    ("The launcher forwards port 8143 on your computer through SSH, and opens it in your browser.",
     "The launcher forwards port eighty-one forty-three on your computer through S S H, and opens it in your browser.", None, "ssh1", FULL, "ssh1:out"),
  ]},
  {"title": "-ssh in the browser", "label": "OFE-GUI · -ssh", "sentences": [
    ("Everything on this page now runs on the remote host.",
     None, None, "ssh", GUI_ALL, None),
    ("The Terminal is a shell on forky, an arm64 server, in the folder we chose.",
     "The Terminal is a shell on forky, an arm sixty-four server, in the folder we chose.", None, "ssh", (1050, 120, 1900), (1196, 266, 2570, 470)),
    ("Choose files uploads data from your computer into that folder; Choose on forky picks files already there.",
     "Choose files uploads data from your computer into that folder; Choose on forky, picks files already there.", None, "ssh", (0, 130, 1300), (16, 538, 1132, 656)),
    ("The fit runs there too, with the same result: T1 is 1.998, plus or minus 0.030.",
     "The fit runs there too, with the same result: T one is one point nine nine eight, plus or minus zero point zero three zero.", 1.22, "ssh", (2000, 1100, 1840), (2640, 1840, 3800, 1910)),
  ]},
  {"title": "-ssh options", "label": None, "sentences": [
    ("A few options shape the remote session.",
     None, None, "ssh2", FULL, None),
    ("Give each account or server its own remote address, so that sessions never collide.",
     None, None, "ssh2", FULL, "ssh2:addr"),
    ("An idle timeout stops the remote OFE-GUI once nobody has used it for a while.",
     "An idle timeout stops the remote O F E GUI, once nobody has used it for a while.", None, "ssh2", FULL, "ssh2:idle"),
    ("Your SSH configuration applies as usual: host aliases, keys, agents and jump hosts.",
     "Your S S H configuration applies as usual: host aliases, keys, agents, and jump hosts.", None, "ssh2", FULL, "ssh2:sshcfg"),
    ("Close the launcher, or lose the connection, and the remote OFE-GUI stops too.",
     "Close the launcher, or lose the connection, and the remote O F E GUI stops too.", None, "ssh2", FULL, "ssh2:stop"),
  ]},
  {"title": "-connect-remote", "label": None, "sentences": [
    ("-connect-remote divides the work differently.",
     "Dash connect remote divides the work differently.", None, "connect1", FULL, None),
    ("OFE-GUI runs on your computer, and a second OFE-GUI is started on the remote host, behind an SSH tunnel.",
     "O F E GUI runs on your computer; and a second O F E GUI is started on the remote host, behind an S S H tunnel.", None, "connect1", FULL, "connect1:net"),
    ("The launcher reports both, each on its own address.",
     None, None, "connect1", FULL, "connect1:cmd"),
  ]},
  {"title": "-connect-remote in the browser", "label": "OFE-GUI · -connect-remote", "sentences": [
    ("In Settings, the Remote onefite-gui field already holds the tunnel's address.",
     "In Settings, the Remote field already holds the tunnel's address.", None, "connect", (0, 100, 1700), (10, 378, 822, 432)),
    ("The Terminal and the files stay on your computer, here in the fits folder.",
     None, None, "connect", (1500, 120, 1700), (1792, 266, 2840, 450)),
    ("Only the fit goes to the remote host, and its results come back here.",
     None, None, "connect", (2140, 700, 1700), (2905, 905, 3830, 1500)),
    ("Clear the field, and the next fit runs locally.",
     None, None, "connect", (0, 100, 1700), (10, 378, 822, 432)),
  ]},
  {"title": "An OFE-GUI already running", "label": None, "sentences": [
    ("If OFE-GUI already runs on the server, for example as a system service, open the tunnel yourself.",
     "If O F E GUI already runs on the server, for example as a system service, open the tunnel yourself.", None, "manual", FULL, "manual:tunnel"),
    ("Then open its address in your browser, as with -ssh,",
     "Then open its address in your browser, as with dash S S H;", None, "manual", FULL, "manual:browser"),
    ("or put it in the Remote onefite-gui field of your own OFE-GUI, as with -connect-remote.",
     "or put it in the Remote field of your own O F E GUI, as with dash connect remote.", None, "manual", FULL, "manual:field"),
  ]},
  {"title": "-reverse-ssh", "label": None, "sentences": [
    ("Sometimes the computer that runs the fits is behind NAT or a firewall, and can't accept connections.",
     "Sometimes the computer that runs the fits is behind N A T, or a firewall, and can't accept connections.", None, "reverse", FULL, None),
    ("With -reverse-ssh, it serves OFE-GUI itself and opens the tunnel outbound, to a computer you can reach.",
     "With dash reverse S S H, it serves O F E GUI itself, and opens the tunnel outbound, to a computer you can reach.", None, "reverse", FULL, "reverse:net"),
    ("On that computer, open 127.0.0.1, port 8143, in the browser.",
     "On that computer, open one two seven, zero, zero, one; port eighty-one forty-three, in the browser.", None, "reverse", FULL, "reverse:cmd"),
  ]},
  {"title": "An engine web service", "label": None, "sentences": [
    ("OFE-GUI can also drive an engine web service directly: in Settings, give the onefite executable an http address.",
     "O F E GUI can also drive an engine web service directly: in Settings, give the engine executable an H T T P address.", None, "engine", FULL, ["engine:exe", "engine:exe_v"]),
    ("That service comes from the Raku engine, started with onefite start-web-engine.",
     "That service comes from the Raku engine, started with its start web engine command.", None, "engine", FULL, ["engine:raku", "engine:raku_v"]),
    ("Its interface is smaller: one data file per fit and fewer options, and anything unsupported is reported, never silently dropped.",
     None, None, "engine", FULL, ["engine:less", "engine:less_v"]),
  ]},
  {"title": "Which one?", "label": None, "sentences": [
    ("So choose by where things should run.",
     None, None, "choose", FULL, None),
    ("-ssh puts everything on the remote host.",
     "Dash S S H puts everything on the remote host.", None, "choose", FULL, ["choose:ssh", "choose:ssh_v"]),
    ("-connect-remote keeps the interface here, and sends the fits there.",
     "Dash connect remote keeps the interface here, and sends the fits there.", None, "choose", FULL, ["choose:connect", "choose:connect_v"]),
    ("A tunnel reaches an OFE-GUI that is already running.",
     "A tunnel reaches an O F E GUI that is already running.", None, "choose", FULL, ["choose:tunnel", "choose:tunnel_v"]),
    ("-reverse-ssh works when the fitting machine can't be reached.",
     "Dash reverse S S H works when the fitting machine can't be reached.", None, "choose", FULL, ["choose:reverse", "choose:reverse_v"]),
    ("In every case OFE-GUI listens only on 127.0.0.1, and SSH does the connecting.",
     "In every case, O F E GUI listens only on the local address, and S S H does the connecting.", None, "choose", FULL, "choose:safe"),
  ]},
  {"title": "Closing", "label": None, "sentences": [
    ("onefite-gui -h lists every option, and its manual page describes them all.",
     "The help option lists every option, and the manual page describes them all.", None, "close", FULL, None),
    ("Both OFE-Go and OFE-GUI are currently distributed under the Artistic License 2.0.",
     "Both O F E Go and O F E GUI are currently distributed under the Artistic License two point zero.", None, "close", FULL, None),
    ("A separate commercial license for eligible project code is in preparation.",
     None, None, "close", FULL, None),
  ]},
]
