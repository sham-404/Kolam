import 'dart:ui' as ui;
import 'dart:math';
import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import 'dart:async';

// --- DATA STRUCTURES ---

class Tile {
  ui.Image img;
  List<String> edges;
  int index; // The final index in the master `tiles` list
  int baseIndex; // The index of the original tile it was rotated from

  List<int> up = [], right = [], down = [], left = [];

  Tile({
    required this.img,
    required this.edges,
    required this.index,
    required this.baseIndex,
  });

  // Helper to compare edges (Python's tile[::-1])
  bool compareEdge(String a, String b) {
    return a == b.split('').reversed.join('');
  }

  void analyze(List<Tile> tiles) {
    for (int i = 0; i < tiles.length; i++) {
      final other = tiles[i];
      if (compareEdge(edges[0], other.edges[2])) up.add(i);
      if (compareEdge(edges[1], other.edges[3])) right.add(i);
      if (compareEdge(edges[2], other.edges[0])) down.add(i);
      if (compareEdge(edges[3], other.edges[1])) left.add(i);
    }
  }

  // Rotates the tile and its edges. Image rotation is async.
  Future<Tile> rotate(int num, int newBaseIndex) async {
    final recorder = ui.PictureRecorder();
    final canvas = Canvas(recorder);
    final pivot = Offset(img.width / 2, img.height / 2);

    canvas.translate(pivot.dx, pivot.dy);
    canvas.rotate(num * pi / 2); // pi/2 is 90 degrees
    canvas.translate(-pivot.dx, -pivot.dy);
    canvas.drawImage(img, Offset.zero, Paint());

    final picture = recorder.endRecording();
    final newImg = await picture.toImage(img.width, img.height);

    final len = edges.length;
    final newEdges = List.generate(len, (i) => edges[(i - num + len) % len]);

    return Tile(img: newImg, edges: newEdges, index: -1, baseIndex: newBaseIndex);
  }
}

class Cell {
  bool collapsed = false;
  List<int> options;

  Cell(int numOptions) : options = List.generate(numOptions, (i) => i);
  Cell.fromList(this.options);
}

// --- CONFIGURATION ---

const List<List<String>> baseEdges = [
  ["000", "010", "010", "000"],
  ["010", "010", "010", "000"],
  ["010", "010", "010", "010"],
  ["000", "010", "000", "000"],
  ["010", "000", "010", "000"],
];
const int imageCount = 5;
const String tilePath = "assets/tiles/KolamTiles1";
const int dim = 10; // Changed back to 15 to match original python

// --- CONTROLLER ---

class WfcController extends ChangeNotifier {
  List<Tile> tiles = [];
  List<double> tileWeights = [];
  List<Cell> grid = [];
  List<ui.Image> tileImages = [];
  bool isInitialized = false;

  WfcController() {
    _init();
  }

  Future<void> _init() async {
    await _loadTileImages();
    await _setupTiles();
    startOver();
    isInitialized = true;
    notifyListeners();
  }

  Future<void> _loadTileImages() async {
    for (int i = 0; i < imageCount; i++) {
      final ByteData data = await rootBundle.load('$tilePath/$i.png');
      final ui.Codec codec = await ui.instantiateImageCodec(data.buffer.asUint8List());
      final ui.FrameInfo fi = await codec.getNextFrame();
      tileImages.add(fi.image);
    }
  }

  Future<void> _setupTiles() async {
    // 1. Create base tiles
    List<Tile> baseTiles = [];
    for (int i = 0; i < baseEdges.length; i++) {
      baseTiles.add(Tile(
          img: tileImages[i], edges: baseEdges[i], index: i, baseIndex: i));
    }

    // 2. Generate all rotations for each base tile
    List<Tile> allRotatedTiles = [];
    for (int i = 0; i < baseTiles.length; i++) {
      final t = baseTiles[i];
      Map<String, Tile> uniqueRotations = {};
      for (int rot = 0; rot < 4; rot++) {
        var rotatedTile = await t.rotate(rot, i);
        final key = rotatedTile.edges.join(',');
        uniqueRotations.putIfAbsent(key, () => rotatedTile);
      }
      allRotatedTiles.addAll(uniqueRotations.values);
    }

    // 3. De-duplicate across all tiles
    Map<String, Tile> finalUniqueTiles = {};
    for (final tile in allRotatedTiles) {
      final key = tile.edges.join(',');
      finalUniqueTiles.putIfAbsent(key, () => tile);
    }
    tiles = finalUniqueTiles.values.toList();

    // 4. Assign final indices and analyze adjacencies
    for (int i = 0; i < tiles.length; i++) {
      tiles[i].index = i;
    }
    for (final tile in tiles) {
      tile.analyze(tiles);
    }

    // 5. Initialize weights (all equally likely for now)
    tileWeights = List.generate(tiles.length, (_) => 1.0);
    print("Tiles after rotation/dedupe: ${tiles.length}");
  }

  void startOver() {
    if (tiles.isEmpty) return;
    grid = List.generate(dim * dim, (index) => Cell(tiles.length));
    notifyListeners();
  }

  void step() {
    if (grid.every((c) => c.collapsed) || tiles.isEmpty) return;
    _collapseOne();
    _updateNeighbors();
    notifyListeners();
  }

  void _collapseOne() {
    var nonCollapsed = grid.where((c) => !c.collapsed).toList();
    if (nonCollapsed.isEmpty) return;

    double minEntropy = double.infinity;
    Cell? chosenCell;

    for (final cell in nonCollapsed) {
      if (cell.options.length < 2) continue;

      double sumOfWeights = 0;
      double sumOfWeightLogs = 0;
      for (final option in cell.options) {
        final weight = tileWeights[option];
        sumOfWeights += weight;
        sumOfWeightLogs += weight * log(weight);
      }

      double entropy = log(sumOfWeights) - (sumOfWeightLogs / sumOfWeights);
      entropy += Random().nextDouble() * 0.001; // Add noise to break ties

      if (entropy < minEntropy) {
        minEntropy = entropy;
        chosenCell = cell;
      }
    }
    
    // Fallback if no cell was chosen via entropy (e.g. all have 1 option)
    chosenCell ??= nonCollapsed.firstWhere((c) => c.options.length > 1, orElse: ()=> nonCollapsed.first);


    chosenCell.collapsed = true;
    
    if (chosenCell.options.isEmpty) {
        startOver(); return;
    }

    double totalWeight = 0;
    for (final option in chosenCell.options) {
      totalWeight += tileWeights[option];
    }
    double randVal = Random().nextDouble() * totalWeight;
    int pick = chosenCell.options.last;
    for (final option in chosenCell.options) {
      randVal -= tileWeights[option];
      if (randVal < 0) {
        pick = option;
        break;
      }
    }
    chosenCell.options = [pick];
  }

  void _updateNeighbors() {
    List<Cell?> nextGrid = List.filled(dim * dim, null);
    for (int j = 0; j < dim; j++) {
      for (int i = 0; i < dim; i++) {
        final idx = i + j * dim;
        if (grid[idx].collapsed) {
          nextGrid[idx] = grid[idx];
        } else {
          List<int> options = List.generate(tiles.length, (k) => k);
          // UP
          if (j > 0) {
            final up = grid[i + (j - 1) * dim];
            final valid = <int>{};
            up.options.forEach((opt) => valid.addAll(tiles[opt].down));
            options.retainWhere((opt) => valid.contains(opt));
          }
          // RIGHT
          if (i < dim - 1) {
            final right = grid[i + 1 + j * dim];
            final valid = <int>{};
            right.options.forEach((opt) => valid.addAll(tiles[opt].left));
            options.retainWhere((opt) => valid.contains(opt));
          }
          // DOWN
          if (j < dim - 1) {
            final down = grid[i + (j + 1) * dim];
            final valid = <int>{};
            down.options.forEach((opt) => valid.addAll(tiles[opt].up));
            options.retainWhere((opt) => valid.contains(opt));
          }
          // LEFT
          if (i > 0) {
            final left = grid[i - 1 + j * dim];
            final valid = <int>{};
            left.options.forEach((opt) => valid.addAll(tiles[opt].right));
            options.retainWhere((opt) => valid.contains(opt));
          }

          if (options.isEmpty) {
            print("[WFC] Contradiction found - restarting");
            startOver();
            return;
          }
          nextGrid[idx] = Cell.fromList(options);
        }
      }
    }
    grid = nextGrid.cast<Cell>();
  }
}