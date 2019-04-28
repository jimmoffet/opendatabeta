var g = {
    nodes: [],
    edges: []
};

// sigma.classes.graph.addMethod('iterNodes', function() {
//   return this.nodes();
// });


var sigInst, canvas, $GP
var config = {};

var dom;


//sigInst = s;

function isSafari() {
    var ua = navigator.userAgent.toLowerCase();
    if (ua.indexOf('safari') != -1) {
        if (ua.indexOf('chrome') > -1) {
            return false;
        } else {
            return true;
        }
    }
    return false;
}

function wamuGetBrowserName() {
    var $browserName;
    if (navigator.userAgent.match(/Android/i)) {
        $browserName = "Android";
    } else if (navigator.userAgent.match(/webOS/i)) {
        $browserName = "webOS";
    } else if (navigator.userAgent.match(/iPhone/i)) {
        $browserName = "iPhone";
    } else if (navigator.userAgent.match(/iPad/i)) {
        $browserName = "iPad";
    } else if (navigator.userAgent.match(/iPod/i)) {
        $browserName = "iPod";
    } else if (navigator.userAgent.match(/BlackBerry/i)) {
        $browserName = "BlackBerry";
    } else {
        $browserName = "Other";
    }
    $browserName = $browserName.toLowerCase();
    return $browserName;
}

function getEdgeSize(a, b) {
    var edgeSize = 0;
    var edgeAmount = 0.0;
    sigInst.graph.edges().forEach(function(h) {
        if ((h.source == a && h.target == b) || (h.source == b && h.target == a)) {
            edgeSize = h.size;
            edgeAmount = h.amount;
        }
    });
    return [edgeSize, edgeAmount];
}

function getNodeID(labelName) {
    var nodeID = 0;
    //console.log('GETNODEID LOOP IS RUNNING ON'+labelName);
    sigInst.graph.nodes().forEach(function(a) {

        if (a.label == labelName) {
            nodeID = a.id;
            //console.log('found a match, returning '+ a.id);

        }
    });
    //console.log('for real tho, returning '+ nodeID);
    return nodeID;
}

function GetQueryStringParams(sParam, defaultVal) {
    var sPageURL = "" + window.location;
    if (sPageURL.indexOf("?") == -1) return defaultVal;
    sPageURL = sPageURL.substr(sPageURL.indexOf("?") + 1);
    var sURLVariables = sPageURL.split('&');
    for (var i = 0; i < sURLVariables.length; i++) {
        var sParameterName = sURLVariables[i].split('=');
        if (sParameterName[0] == sParam) {
            return sParameterName[1];
        }
    }
    return defaultVal;
}

if (wamuGetBrowserName() == "other") {
    jQuery.getJSON(GetQueryStringParams("config", "https://s3.us-east-2.amazonaws.com/opendatabeta/config.json"), function(data, textStatus, jqXHR) {
        config = data;
        if (config.type != "network") {
            alert("Invalid configuration settings.")
            return;
        }
        $(document).ready(setupGUI(config));
    });
} else {
    jQuery.getJSON(GetQueryStringParams("config", "https://s3.us-east-2.amazonaws.com/opendatabeta/config.mob.json"), function(data, textStatus, jqXHR) {
        config = data;
        if (config.type != "network") {
            alert("Invalid configuration settings.")
            return;
        }
        $(document).ready(setupGUI(config));
    });
}

Object.size = function(obj) {
    var size = 0,
        key;
    for (key in obj) {
        if (obj.hasOwnProperty(key)) size++;
    }
    return size;
};

function initSigma(config) {
    var data = config.data;
    var a = new sigma({ 
    graph: g,
    renderer: {
        container: document.getElementById('sigma-canvas'),
        type: 'canvas'
    },
    settings: {
        // GRAPH SETTINGS
        verbose: true, 
        }
    });

    a.settings({
        // NODE SETTINGS
        defaultNodeColor: '#666',
        minNodeSize: 1,
        maxNodeSize: 20,
        doubleClickEnabled: false,

        // LABEL SETTINGS
        defaultLabelColor: "#444",
        defaultLabelSize: 13,
        defaultLabelBGColor: "#ddd",
        defaultHoverLabelBGColor: "#002147",
        defaultLabelHoverColor: "#fff",
        activeFontStyle: "bold",
        labelThreshold: 12,
        //labelSize: proportional,
        labelSizeRatio: 1.5,
        //fontStyle: "bold",

        // EDGE SETTINGS
        //defaultEdgeColor: '#999',
        //batchEdgesDrawing: true,
        //hideEdgesOnMove: true,
        defaultEdgeType: 'curve',
        //edgeColor: 'default',
        //edgeLabelSize: 'proportional',
        minEdgeSize: 0.1,
        maxEdgeSize: 12,
        
        // HOVERS
        hoverFontStyle: "bold",
        // enableEdgeHovering: true,
        // edgeHoverColor: 'edge',
        // defaultEdgeHoverColor: '#000',
        // edgeHoverSizeRatio: 1,
        // edgeHoverExtremities: true, 

        // ZOOM SETTINGS
        zoomingRatio: 1.2,
        mouseZoomDuration: 1,
        mouseInteriaRatio: 1

    });

    // var a = new sigma();

    // cam = a.addCamera();

    a.active = !1;
    a.neighbors = {};
    a.detail = !1;
    dataReady = function() {
        
        a.clusters = {};
        //console.log('DATAREADY LOOP IS RUNNING');
        a.graph.nodes().forEach(function(b) {
            a.clusters[b.color] || (a.clusters[b.color] = []);
            a.clusters[b.color].push(b.id);
        });

        a.camera.goTo({
            x: a.camera.x,
            y: a.camera.y,
            ratio: 0.75,
            angle: 1.5
        });

        a.bind('clickNode doubleClickNode rightClickNode', function(e) {
            //console.log(e.type, e.data.node.label, e.data.captor);
            nodeActive(e.data.node.id);
        });

        a.bind('overEdge', function(e) {
          console.log(e.data.edge.id, e.data.edge.type);
        });

        // // NEEDS TO BE CLICK BUT NOT DRAG
        // a.bind('clickStage', function(e) {
        //     showFull()
        // });

        a.refresh();
        configSigmaElements(config);
    }

    if (data.indexOf("gexf") > 0 || data.indexOf("xml") > 0)
        a.parseGexf(data, dataReady);
    else {
        //sigma.parsers.json(data, dataReady);
        //console.log(a.graph.iterNodes());
        sigma.parsers.json(data, a, dataReady);
        gexf = sigmaInst = null;
    }

    a.refresh();
    s = a;
    sigInst = a;
    
}

function setupGUI(config) {
    var logo = "";
    if (config.logo.file) {
        logo = "<img src=\"" + config.logo.file + "\"";
        if (config.logo.text) logo += " alt=\"" + config.logo.text + "\"";
        logo += ">";
    } else if (config.logo.text) {
        logo = "<h1>" + config.logo.text + "</h1>";
    }
    if (config.logo.link) logo = "<a href=\"" + config.logo.link + "\">" + logo + "</a>";
    $("#maintitle").html(logo);
    $("#title").html("<h2>" + config.text.title + "</h2>");
    $("#titletext").html(config.text.intro);
    if (config.text.more) {
        $("#information").html(config.text.more);
    } else {
        $("#moreinformation").hide();
    }
    if (config.legend.nodeLabel) {
        $(".node").next().html(config.legend.nodeLabel);
    } else {
        $(".node").hide();
    }
    if (config.legend.edgeLabel) {
        $(".edge").next().html(config.legend.edgeLabel);
    } else {
        $(".edge").hide();
    }
    if (config.legend.nodeLabel) {
        $(".colors").next().html(config.legend.colorLabel);
    } else {
        $(".colors").hide();
    }
    $GP = {
        calculating: !1,
        showgroup: !1
    };
    $GP.intro = $("#intro");
    $GP.minifier = $GP.intro.find("#minifier");
    $GP.mini = $("#minify");
    $GP.info = $("#attributepane");
    $GP.main = $("#mainpanel");
    $GP.info_header = $GP.info.find(".mainheader");
    $GP.info_details = $GP.info.find(".details");
    $GP.info_image = $GP.info.find(".image");
    $GP.info_donnees = $GP.info.find(".nodeattributes");
    $GP.info_name = $GP.info.find(".name");
    $GP.info_link = $GP.info.find(".link");
    $GP.info_data = $GP.info.find(".data");
    $GP.info_close = $GP.info.find(".returntext");
    $GP.info_close2 = $GP.info.find(".close");
    $GP.main_hide = $GP.main.find(".hide");
    $GP.mainpanel = $GP.main.find(".col");
    $GP.info_p = $GP.info.find(".p");
    $GP.info_close.click(function() {
        $GP.info.delay(50).animate({
            width: 'hide'
        }, 50);
    });
    $GP.info_close2.click(function() {
        $GP.info.delay(50).animate({
            width: 'hide'
        }, 50);
    });
    $GP.main_hide.toggle(function() {
        $GP.main.delay(1).animate({
            left: '-250px'
        }, 50);
    }, function() {
        $GP.main.delay(1).animate({
            left: '0px'
        }, 50);
    });
    $GP.form = $("#mainpanel").find("form");
    $GP.search = new Search($GP.form.find("#search"));
    if (!config.features.search) {
        $("#search").hide();
    }
    if (!config.features.groupSelectorAttribute) {
        $("#attributeselect").hide();
    }
    $GP.cluster = new Cluster($GP.form.find("#attributeselect"));
    config.GP = $GP;
    initSigma(config);
    cleanPanel();
    showKey();
    $('#zoom .z[rel="full"]').addClass('inactive');
    $('#zoom .z[rel="details"]').addClass('inactive');
    dom = document.querySelector('#sigma-canvas canvas:last-child');
}



function configSigmaElements(config) {

    $GP = config.GP;

    console.log('CONFIGSIGMA LOOP IS RUNNING');

    var a = [],
        b, x = 1;
    for (b in sigInst.clusters) {
        cName = "";
        if (b == "rgb(255,179,188)") {
            cName = "Former Officials";
        } else if (b == "rgb(184,184,184)") {
            cName = "Developers";
        } else if (b == "rgb(250,0,45)") {
            cName = "Officials Currently in Office";
        }
        a.push('<div style="line-height:12px"><a href="#' + b + '"><div style="width:40px;height:12px;border:1px solid #fff;background:' + b + ';display:inline-block"></div> ' + cName + ' (' + sigInst.clusters[b].length + ')</a></div>');
    }

    $GP.cluster.content(a.join(""));

    b = {
        minWidth: 400,
        maxWidth: 800,
        maxHeight: 600
    };

    var r = 1;

    function zoomTo(b) {
        r *= (b == "in" ? 0.8 : 1.1)
        sigInst.camera.goTo({
            x: sigInst.camera.x,
            y: sigInst.camera.y,
            ratio: r
        });
    }

    $("a.fb").fancybox(b);
    $("#zoom").find("div.z").each(function() {
        var a = $(this),
            b = a.attr("rel");
        a.click(function() {
            if (b == "center") {
                sigInst.position(0, 0, 1).draw();
            } else if (b == "details") {
                showDetails();
            } else if (b == "full") {
                showFull();
                console.log('showFull and showKey were CALLED inside config sigma');
                showKey();
            } else if (b == "key") {
                showKey();
            } else if (b != "spacer") {
                zoomTo(b)
            }
        })
    });

    $GP.mini.click(function() {
        $GP.mini.hide();
        $GP.intro.show();
        $GP.minifier.show()
    });

    $GP.minifier.click(function() {
        $GP.intro.hide();
        $GP.minifier.hide();
        $GP.mini.show()
    });

    $GP.intro.find("#showGroups").click(function() {
        !0 == $GP.showgroup ? showGroups(!1) : showGroups(!0)
    });

    a = window.location.hash.substr(1);

    if (0 < a.length) switch (a) {
        case "Groups":
            showGroups(!0);
            break;
        case "information":
            $.fancybox.open($("#information"), b);
            break;
        default:
            $GP.search.exactMatch = !0, $GP.search.search(a)
            $GP.search.clean();
    }
}

function Search(a) {
    this.input = a.find("input[name=search]");
    this.state = a.find(".state");
    this.results = a.find(".results");
    this.exactMatch = !1;
    this.lastSearch = "";
    this.searching = !1;
    var b = this;
    this.input.focus(function() {
        var a = $(this);
        a.data("focus") || (a.data("focus", !0), a.removeClass("empty"));
        b.clean()
    });
    this.input.keydown(function(a) {
        if (13 == a.which) return b.state.addClass("searching"), b.search(b.input.val()), !1
    });
    this.state.click(function() {
        var a = b.input.val();
        b.searching && a == b.lastSearch ? (b.close(), $('#zoom .z[rel="key"]').removeClass('active')) : (b.state.addClass("searching"), b.search(a))
    });
    this.dom = a;
    this.close = function() {
        this.state.removeClass("searching");
        this.results.hide();
        this.searching = !1;
        this.input.val("");
        nodeNormal()
    };
    this.clean = function() {
        this.results.empty().hide();
        this.state.removeClass("searching");
        this.input.val("");
    };
    this.search = function(a) {
        var b = !1,
            c = [],
            b = this.exactMatch ? ("^" + a + "$").toLowerCase() : a.toLowerCase(),
            g = RegExp(b);
        this.exactMatch = !1;
        this.searching = !0;
        this.lastSearch = a;
        this.results.empty();
        if (2 >= a.length) this.results.html("<i>You must search for a name with a minimum of 3 letters.</i>");
        else {
            sigInst.graph.nodes().forEach(function(a) {
                //console.log('SEARCH LOOP IS RUNNING');
                g.test(a.label.toLowerCase()) && c.push({
                    id: a.id,
                    name: a.label
                })
            });
            c.length ? (b = !0, nodeActive(c[0].id)) : b = showCluster(a);
            a = ["<b>Search Results: </b>"];
            if (1 < c.length)
                for (var d = 0, h = c.length; d < h; d++) a.push('<a href="#' + c[d].name + '" onclick="nodeActive(\'' + c[d].id + "')\">" + c[d].name + "</a>");
            0 == c.length && !b && a.push("<i>No results found.</i>");
            1 < a.length && this.results.html(a.join(""));
        }
        if (c.length != 1) this.results.show();
        if (c.length == 1) this.results.hide();
    }
}

function Cluster(a) {
    this.cluster = a;
    this.display = !1;
    this.list = this.cluster.find(".list");
    this.list.empty();
    this.select = this.cluster.find(".select");
    this.select.click(function() {
        $GP.cluster.toggle()
    });
    this.toggle = function() {
        this.display ? this.hide() : this.show()
    };
    this.content = function(a) {
        this.list.html(a);
        this.list.find("a").click(function() {
            var a = $(this).attr("href").substr(1);
            showCluster(a)
        })
    };
    this.hide = function() {
        this.display = !1;
        this.list.hide();
        this.select.removeClass("close")
    };
    this.show = function() {
        this.display = !0;
        this.list.show();
        this.select.addClass("close")
    }
}


// swap visibility of groups, maybe can use div id = cf ???
function showGroups(a) {
    a ? ($GP.intro.find("#showGroups").text("Hide groups"), 
        //$GP.bg.show(), 
        //$GP.bg2.hide(), 
        $GP.showgroup = !0) : ($GP.intro.find("#showGroups").text("View Groups"), 
        //$GP.bg.hide(), 
        //$GP.bg2.show(), 
        $GP.showgroup = !1)
}

function nodeNormal() {
    console.log('nodeNormal WAS CALLED');
    !0 != $GP.calculating && !1 != sigInst.detail && (showGroups(!1), 
    $GP.calculating = !0, 
    sigInst.detail = !0, 
    $GP.info.delay(0).animate({ width: 'hide' }, 0), 
    $GP.cluster.hide(), 
    sigInst.graph.edges().forEach(function(a) {
        //a.color = !1;
        a.hidden = !1,
        a.type = 'curve'
    }), 
    sigInst.graph.nodes().forEach(function(a) {
        a.hidden = !1;
        //a.color = !1;
        //a.lineWidth = !1;
        //a.size = !1
    }), 
    // sigInst.draw(2, 2, 2, 2), 
    // sigInst.camera.goTo(2, 2, 2, 2), 
    sigInst.refresh(),
    sigInst.neighbors = {}, 
    sigInst.active = !1, 
    $GP.calculating = !1, 
    window.location.hash = "")

    $('#zoom .z[rel="details"]').addClass('inactive');
    $('#zoom .z[rel="full"]').addClass('inactive');
    console.log('showKey WAS CALLED inside nodeNormal');
    showKey();

}

function nodeActive(a) {
    console.log('nodeActivate was called');
    $('#zoom .z[rel="full"]').removeClass('inactive');
    $('#zoom .z[rel="details"]').removeClass('inactive');
    cleanPanel();
    var groupByDirection = false;
    if (config.informationPanel.groupByEdgeDirection && config.informationPanel.groupByEdgeDirection == true) groupByDirection = true;
    sigInst.neighbors = {};
    sigInst.detail = !0;
    //var b = sigInst.graph.nodes()[a];
    sigInst.graph.nodes().forEach(function(n) {
        if (n.id == a) {
            b = n;
        }
    });
    showGroups(!1);
    var outgoing = {},
        incoming = {},
        mutual = {};
    
    sigInst.graph.edges().forEach(function(b) {
        b.type = 'curve';
        b.hidden = !0;
        n = {
            name: b.label,
            color: b.color
        };
        if (a == b.source) outgoing[b.target] = n;
        else if (a == b.target) incoming[b.source] = n;
        if (a == b.source || a == b.target) sigInst.neighbors[a == b.target ? b.source : b.target] = n; b.hidden = !1, b.color = b.color;
    });

    var f = [];

    //console.log('a is currently: '+a.label);

    // THIS HIDES ALL NODES
    sigInst.graph.nodes().forEach(function(a) {
        a.hidden = !0;
        //a.lineWidth = !1;
        //a.color = a.color;
    });

    if (groupByDirection) {
        for (e in outgoing) {
            if (e in incoming) {
                mutual[e] = outgoing[e];
                delete incoming[e];
                delete outgoing[e];
            }
        }
    }

    // THIS CREATES A LIST OF NEIGHBOR NODES
    var createList = function(c) {

        var f = [];
        var e = [],
            g;
        for (g in c) {

            //var d = sigInst.graph.nodes()[g];
            var d;
            sigInst.graph.nodes().forEach(function(a) {

                if (a.id == g) {
                    d = a;
                    //console.log('create a match, returning '+ a.id);
                }
            });

            // THIS UNHIDES THE NEIGHBOR NODES
            d.hidden = !1;
            d.lineWidth = !1;
            //d.color = c[g].color;
            //console.log(c[g].color); // c[g].color is black...
            var edgeVals = getEdgeSize(a, g);
            a != g && e.push({
                id: g,
                name: d.label,
                group: (c[g].name) ? c[g].name : "",
                //color: c[g].color,
                size: edgeVals[0],
                amount: edgeVals[1],
                type: 'curve'
            })
        }

        e.sort(function(a, b) {
            var c = a.amount;
            //console.log('a looks like '+a.amount);
            var d = b.amount;
            //console.log('b looks like '+b.amount);
            var e = a.size;
            var f = b.size;
            //console.log('c is '+c+', d is '+d+', e is '+e+', f is '+f);
            return (c != d) ? (c > d) ? -1 : (c < d) ? 1 : 0 : (e > f) ? -1 : (e < f) ? 1 : 0
        });

        //console.log('sorted e looks like '+e.label);

        d = "";
        for (g in e) {
            c = e[g];
            var contribution = "contribution";
            if (c.size > 1) {
                contribution = "contributions";
            }

            f.push('<li class="membership"><a href="#' + c.name + '\" onclick=\"nodeActive(\'' + c.id + '\')" onmouseout="sigInst.refresh()"><b>' + c.name + '</b></a><div class="bar" style="width:' + (((c.amount / e[0].amount) * 100)) + '%;">' + '</div><sub><b>' + c.size + '</b> ' + contribution + ' totalling' + '<b> $' + c.amount.toFixed(2).toString().replace(/\B(?=(\d{3})+(?!\d))/g, ",") + '</b></sub></li>');
        
        }
        return f;
    }
    var f = [];
    if (groupByDirection) {
        size = Object.size(mutual);
        f.push("<h2>Mututal (" + size + ")</h2>");
        (size > 0) ? f = f.concat(createList(mutual)): f.push("No mutual links<br>");
        size = Object.size(incoming);
        f.push("<h2>Incoming (" + size + ")</h2>");
        (size > 0) ? f = f.concat(createList(incoming)): f.push("No incoming links<br>");
        size = Object.size(outgoing);
        f.push("<h2>Outgoing (" + size + ")</h2>");
        (size > 0) ? f = f.concat(createList(outgoing)): f.push("No outgoing links<br>");
    } else {
        f = f.concat(createList(sigInst.neighbors));
    }

    b.hidden = !1;
    
    // b.color = b.color;
    // b.lineWidth = 6;
    // b.strokeStyle = "#000000";
    //b.lineWidth = 6;
    //b.strokeStyle = "#000000";

    //sigInst.camera.goTo(2, 2, 2, 2);
    $GP.info_link.find("ul").html(f.join(""));
    $GP.info_link.find("li").each(function() {
        var a = $(this),
            b = a.attr("rel");
    });
    //f = b.attr;
    f = b;

    //console.log('b is hosed: '+b.label);

    var min_year = 0;
    var max_year = 0;
    if (f.attributes) {
        var image_attribute = false;
        if (config.informationPanel.imageAttribute) {
            image_attribute = config.informationPanel.imageAttribute;
        }
        e = [];
        q = [];
        r = [];
        temp_array = [];
        g = 0;
        var candidate = true;
        if (b.attributes.Title == 'Developer') {
            candidate = false;
        }
        for (var attr in f.attributes) {
            var d = f.attributes[attr],
                h = "";
            if (attr == "Title") {
                q.push('<br/>' + d);
            } else if (attr == "Ward") {
                if (d == "At Large") {
                    q.push(', ' + d);
                } else {
                    q.push(', Ward ' + d);
                }
            } else if (attr == "Image") {
                $GP.info_image.html(d);
            } else if (attr == "Total Developer Donations") {
                var direction = " received";
                if (candidate == false) {
                    direction = " given";
                }
                if (d > 1) {
                    r.push('<br/><b>' + d + '</b> contributions' + direction);
                } else {
                    r.push('<br/><b>' + d + '</b> contribution' + direction);
                }
            } else if (attr == "Total Donation Amount") {
                r.push('<br/><b>$' + d.toFixed(2).toString().replace(/\B(?=(\d{3})+(?!\d))/g, ",") + '</b> total');
            } else if (attr == "Min Year") {
                min_year = d;
            } else if (attr == "Max Year") {
                max_year = d;
            } else if (attr != "Incumbent" && attr != "Affiliates Redundant") {
                h = '<div class="p">' + attr + '</div> ' + d + '<br/>'
                e.push(h)
            }
        }
        if (image_attribute) {
            $GP.info_name.html("<div><img src=" + f.attributes[image_attribute] + "style=\"vertical-align:middle\" /> <span>" + b.label + "</span></div>");
        } else {
            q.unshift("<span class='head'>" + b.label + "</span>");
        }
        $GP.info_data.html(e.join("<br/>"));
        $GP.info_name.html(q.join(''));
        $GP.info_details.html(r.join(''));
    }
    $GP.info_data.show();
    $GP.info_p.html('');
    if (min_year == max_year) {
        $GP.info_p.html("Contributions (" + max_year + ")");
    } else {
        $GP.info_p.html("Contributions (" + min_year + "-" + max_year + ")");
    }
    $GP.info.animate({
        width: 'show'
    }, 0);
    $('#zoom .z[rel="details"]').addClass('active');
    $GP.info_donnees.hide();
    $GP.info_donnees.show();
    sigInst.active = a;

    //console.log('Write hash to address: '+b.label);

    window.location.hash = b.label;
    $('.nodeattributes').scrollTop(0);
    delete min_year;
    delete max_year;
    sigInst.refresh();
}

function showCluster(a) {
    cleanPanel();
    console.log('SHOWCLUSTERS LOOP IS RUNNING');
    $('#zoom .z[rel="full"]').removeClass('inactive');
    $('#zoom .z[rel="details"]').removeClass('inactive');
    var b = sigInst.clusters[a];
    if (b && 0 < b.length) {
        showGroups(!1);
        sigInst.detail = !0;
        b.sort(function(a, g) {
            var h = sigInst.graph.nodes()[a];
            var i = sigInst.graph.nodes()[g];
            var c = h.attributes["Total Donation Amount"];
            var d = i.attributes["Total Donation Amount"];
            var e = h.attributes["Total Developer Donations"];
            var f = i.attributes["Total Developer Donations"];
            return (c != d) ? (c > d) ? -1 : (c < d) ? 1 : 0 : (e > f) ? -1 : (e < f) ? 1 : 0
        });
        sigInst.graph.edges().forEach(function(a) {
            a.hidden = !1;
            //a.lineWidth = !1;
            //a.color = !1
        });
        sigInst.graph.nodes().forEach(function(a) {
            console.log('SC HIDDEN LOOP IS RUNNING');
            a.hidden = !0
        });
        console.log('we are looping until '+b.length);
        for (var f = [], e = [], c = 0, g = b.length; c < g; c++) {
            var d = sigInst.graph.nodes()[b[c]];
            var contribution = "contribution";
            if (d.attributes["Total Developer Donations"] > 1) {
                contribution = "contributions";
            }!0 == d.hidden && (e.push(b[c]), d.hidden = !1, d.lineWidth = !1, d.color = d.color, f.push('<li class="membership"><a href="#' + d.label + '" onmouseover="sigInst.plotter.drawHoverNode(sigInst.graph.nodes()[\'' + d.id + '\'])\" onclick=\"nodeActive(\'' + d.id + '\')" onmouseout="sigInst.refresh()"><b>' + d.label + '</b></a><div class="bar" style="width:' + (((d.attributes["Total Donation Amount"] / sigInst.graph.nodes()[b[0]].attributes["Total Donation Amount"]) * 100)) + '%;">' + '</div><sub><b>' + d.attributes["Total Developer Donations"] + '</b> ' + contribution + ' totalling' + ' <b>$' + d.attributes["Total Donation Amount"].toFixed(2).toString().replace(/\B(?=(\d{3})+(?!\d))/g, ",") + '</b></sub></li>'))
        }
        sigInst.clusters[a] = e;
        //sigInst.draw(2, 2, 2, 2);
        sigInst.refresh();
        showDetails();
        cName = '';
        if (a == "rgb(253,149,149)") {
            cName = "Candidates/Former Officials";
        } else if (a == "rgb(137,147,163)") {
            cName = "Developers";
        } else if (a == "rgb(255,0,0)") {
            cName = "Officials Currently in Office";
        }
        $GP.info_name.html('<span class="head">' + cName + '</span>');
        $GP.info_p.html("");
        $GP.info_link.find("ul").html(f.join(""));
        $GP.info.animate({
            width: 'show'
        }, 0);
        $GP.search.clean();
        $GP.cluster.hide();
        $('.nodeattributes').scrollTop(0);
        return !0
    }
    return !1
}

function showKey() {
    console.log('showKey WAS CALLED');
    if (!$GP.info.is(":visible")) {
        $GP.info.delay(0).animate({
            width: 'toggle'
        }, 0);
    }
    $("#zoom .z[rel='details']").removeClass('active');
    if ($('#zoom .z[rel="key"]').hasClass('active')) {
        $('#zoom .z[rel="key"]').removeClass('active');
        $GP.info.delay(0).animate({
            width: 'toggle'
        }, 0);
    } else {
        $('#zoom .z[rel="key"]').addClass('active');
        $GP.info_name.hide();
        $GP.info_image.hide();
        $GP.info_details.hide();
        $('.nodeattributes').hide();
        $GP.info_header.show();
        $('#mainpanel').show();
    }
}

function showDetails() {
    console.log('showDetails WAS CALLED');
    if (sigInst.active !== false || location.hash.indexOf("rgb(") === 1) {
        $("#zoom .z[rel='key']").removeClass('active');
        if (!$GP.info.is(":visible")) {
            $GP.info.delay(0).animate({
                width: 'toggle'
            }, 0);
        }
        if ($('#zoom .z[rel="details"]').hasClass('active')) {
            $('#zoom .z[rel="details"]').removeClass('active');
            $GP.info.delay(0).animate({
                width: 'toggle'
            }, 0);
        } else {
            $('#zoom .z[rel="details"]').addClass('active');
            $('.nodeattributes').show();
            $GP.info_name.show();
            $GP.info_image.show();
            $GP.info_details.show();
            $('#mainpanel').hide();
            $GP.info_header.hide();
        }
    }
}

function showFull() {
    console.log('showFull WAS CALLED');
    if (sigInst.active || location.hash.indexOf('rgb') != -1) {
        nodeNormal();
        if ($('#zoom .z').hasClass('active')) {
            $('#zoom .z').removeClass('active');
        }
    }
    $('#zoom .z[rel="full"]').addClass('inactive');
    $GP.search.clean();
}

function reload() {
    console.log('reload WAS CALLED');
    delete sigma;
    if (wamuGetBrowserName() == "other") {
        jQuery.getJSON(GetQueryStringParams("config", "https://s3.us-east-2.amazonaws.com/opendatabeta/config.json"), function(data, textStatus, jqXHR) {
            config = data;
            if (config.type != "network") {
                alert("Invalid configuration settings.")
                return;
            }
            $(document).ready(setupGUI(config));
        });
    } else {
        jQuery.getJSON(GetQueryStringParams("config", "https://s3.us-east-2.amazonaws.com/opendatabeta/config.mob.json"), function(data, textStatus, jqXHR) {
            config = data;
            if (config.type != "network") {
                alert("Invalid configuration settings.")
                return;
            }
            $(document).ready(setupGUI(config));
        });
    }
}

function cleanPanel() {
    console.log('cleanPanel WAS CALLED');
    $("#mainpanel").hide();
    $GP.info_header.hide();
    $GP.info_data.html('');
    $GP.info_image.html('');
    $GP.info_name.html('');
    $GP.info_details.html('');
    $GP.info_name.show();
    $GP.info_details.show();
    $GP.info_image.show();
    $("#zoom .z[rel='key']").removeClass('active');
}

;(function() {
  'use strict';

  sigma.utils.pkg('sigma.canvas.edges');

  /**
   * This edge renderer will display edges as curves.
   *
   * @param  {object}                   edge         The edge object.
   * @param  {object}                   source node  The edge source node.
   * @param  {object}                   target node  The edge target node.
   * @param  {CanvasRenderingContext2D} context      The canvas context.
   * @param  {configurable}             settings     The settings function.
   */
  sigma.canvas.edges.curve = function(edge, source, target, context, settings) {
    var color = edge.color,
        prefix = settings('prefix') || '',
        size = edge[prefix + 'size'] || 1,
        edgeColor = settings('edgeColor'),
        defaultNodeColor = settings('defaultNodeColor'),
        defaultEdgeColor = settings('defaultEdgeColor'),
        cp = {},
        sSize = source[prefix + 'size'],
        sX = source[prefix + 'x'],
        sY = source[prefix + 'y'],
        tX = target[prefix + 'x'],
        tY = target[prefix + 'y'];

    cp = (source.id === target.id) ?
      sigma.utils.getSelfLoopControlPoints(sX, sY, sSize) :
      sigma.utils.getQuadraticControlPoint(sX, sY, tX, tY);

    if (!color)
      switch (edgeColor) {
        case 'source':
          color = source.color || defaultNodeColor;
          break;
        case 'target':
          color = target.color || defaultNodeColor;
          break;
        default:
          color = defaultEdgeColor;
          break;
      }

    context.strokeStyle = color;
    context.lineWidth = size;
    context.beginPath();
    context.moveTo(sX, sY);
    if (source.id === target.id) {
      context.bezierCurveTo(cp.x1, cp.y1, cp.x2, cp.y2, tX, tY);
    } else {
      context.quadraticCurveTo(cp.x, cp.y, tX, tY);
    }
    context.stroke();
  };
})();


