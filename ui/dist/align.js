import { lusolve, multiply, norm, subtract, transpose } from "mathjs";

export function roiRectInfoToCoordinates(rect, frame) {
  // convert absolute moveable RectInfo to relative coordinates {BL, TL, TR, BR}
  //   -> RdctInfo: https://daybrush.com/moveable/release/latest/doc/Moveable.html#.RectInfo
  return [
    {
      x: (rect.pos3[0] - frame.left) / frame.width,
      y: rect.pos3[1] / frame.height
    },
    {
      x: (rect.pos1[0] - frame.left) / frame.width,
      y: rect.pos1[1] / frame.height
    },
    {
      x: (rect.pos2[0] - frame.left) / frame.width,
      y: rect.pos2[1] / frame.height
    },
    {
      x: (rect.pos4[0] - frame.left) / frame.width,
      y: rect.pos4[1] / frame.height
    }
  ];
}

export function roiCoordinatesToTransform(coordinates, frame) {
  // convert relative coordinates [TL, TR, BL, BR] to CSS matrix3d...
}

export function transform(from, to) {
  // taken from https://franklinta.com/2014/09/08/computing-css-matrix3d-transforms/
  var A, H, b, h, i, j, k, k_i, l, lhs, ref, rhs;
  console.assert(from.length === (ref = to.length) && ref === 4);
  A = []; // 8x8
  for (i = j = 0; j < 4; i = ++j) {
    A.push([
      from[i].x,
      from[i].y,
      1,
      0,
      0,
      0,
      -from[i].x * to[i].x,
      -from[i].y * to[i].x
    ]);
    A.push([
      0,
      0,
      0,
      from[i].x,
      from[i].y,
      1,
      -from[i].x * to[i].y,
      -from[i].y * to[i].y
    ]);
  }
  b = []; // 8x1
  for (i = k = 0; k < 4; i = ++k) {
    b.push(to[i].x);
    b.push(to[i].y);
  }
  // Solve A * h = b for h
  h = lusolve(A, b);
  h = h.reduce((a, b) => a.concat(b), []); // flatten h (is [[...], [...], ...]
  H = [
    [h[0], h[1], 0, h[2]],
    [h[3], h[4], 0, h[5]],
    [0, 0, 1, 0],
    [h[6], h[7], 0, 1]
  ];
  // Sanity check that H actually maps `from` to `to`
  for (i = l = 0; l < 4; i = ++l) {
    lhs = multiply(H, [from[i].x, from[i].y, 0, 1]);
    k_i = lhs[3];
    rhs = multiply(k_i, [to[i].x, to[i].y, 0, 1]);
    let dhs = subtract(lhs, rhs);
    console.assert(norm(dhs) < 1e-9, "Not equal:", lhs, rhs);
  }
  return H;
}

export function toCssMatrix3d(transform) {
  let content = [];
  for (let col = 0; col < 4; col++) {
    // todo: there should be some 'flatten' function; -> flatten(transpose(transform))
    for (let row = 0; row < 4; row++) {
      content = [...content, transform[row][col]];
    }
  }
  return `matrix3d(${content.join(",")})`; // todo: the translation is magix & window size-dependent
  // todo: could set transform, query rect, and get translation ~ position of top left point?
}
