import 'package:flutter/material.dart';
import 'wfc_logic.dart'; // Import our logic
import 'dart:ui' as ui;

class WfcPainter extends CustomPainter {
  final WfcController controller;

  WfcPainter({required this.controller}) : super(repaint: controller);

  @override
  void paint(Canvas canvas, Size size) {
    if (!controller.isInitialized) return;

    final double w = size.width / dim;
    final double h = size.height / dim;

    for (int j = 0; j < dim; j++) {
      for (int i = 0; i < dim; i++) {
        final cell = controller.grid[i + j * dim];
        final rect = Rect.fromLTWH(i * w, j * h, w, h);

        if (cell.collapsed && cell.options.isNotEmpty) {
          final index = cell.options[0];
          final tile = controller.tiles[index];
          // Draw the tile image
          paintImage(
            canvas: canvas,
            rect: rect,
            image: tile.img,
            fit: BoxFit.fill,
          );
        } else {
          // Draw a grid rectangle for an undecided cell
          canvas.drawRect(
            rect,
            Paint()
              ..color = const Color.fromARGB(255, 46, 44, 44)
              ..style = PaintingStyle.stroke,
          );
        }
      }
    }
  }

  @override
  bool shouldRepaint(covariant CustomPainter oldDelegate) => true;
}
