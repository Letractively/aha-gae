addEvent(window, 'load', initCorners);

function initCorners() {
var round4 = {
    tl: { radius: 6 },
    tr: { radius: 6 },
    bl: { radius: 6 },
    br: { radius: 6 },
    antiAlias: true
}

var round2u = {
    tl: { radius: 6 },
    tr: { radius: 6 },
    bl: { radius: 0 },
    br: { radius: 0 },
    antiAlias: true
}

var round2d = {
    tl: { radius: 0 },
    tr: { radius: 0 },
    bl: { radius: 6 },
    br: { radius: 6 },
    antiAlias: true
}

curvyCorners(round4, ".curvy");
curvyCorners(round2u, ".entrytitle");
curvyCorners(round2d, ".entryinfo");

curvyCorners(round2u, ".partstitle");
curvyCorners(round2d, ".partsbody");
}

