import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import 'dart:async'; // For Timer
import 'wfc_logic.dart';
import 'wfc_painter.dart';

void main() {
  runApp(const MyApp());
}

class MyApp extends StatelessWidget {
  const MyApp({super.key});

  @override
  Widget build(BuildContext context) {
    // Provide the controller to the widget tree
    return ChangeNotifierProvider(
      create: (_) => WfcController(),
      child: MaterialApp(
        title: 'Wave Function Collapse (Flutter)',
        theme: ThemeData.dark(),
        
        home: const WfcScreen(),
      ),
    );
  }
}

class WfcScreen extends StatefulWidget {
  const WfcScreen({super.key});

  @override
  State<WfcScreen> createState() => _WfcScreenState();
}

class _WfcScreenState extends State<WfcScreen> {
  Timer? _timer;

  @override
  void initState() {
    super.initState();
    // Start the WFC process automatically
    WidgetsBinding.instance.addPostFrameCallback((_) {
      final controller = Provider.of<WfcController>(context, listen: false);
      _timer = Timer.periodic(const Duration(milliseconds: 16), (timer) {
        if (mounted) {
          controller.step();
        } else {
          timer.cancel();
        }
      });
    });
  }

  @override
  void dispose() {
    _timer?.cancel();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    // Get the controller from the provider
    final controller = context.watch<WfcController>();

    return Scaffold(
      appBar: AppBar(title: const Text('Wave Function Collapse')),
      body: Column(
        children: [
          Expanded(
            // --- NECESSARY CHANGES ARE HERE ---
            child: Center( // 1. Added Center to keep the grid centered
              child: Padding( // 2. Added Padding for breathing room
                padding: const EdgeInsets.all(16.0), // 3. Set the padding amount
                child: AspectRatio(
                  aspectRatio: 1.0,
                  child: CustomPaint(
                    painter: WfcPainter(controller: controller),
                  ),
                ),
              ),
            ),
          ),
          // UI Controls
          Padding(
            padding: const EdgeInsets.all(24),
            child: ElevatedButton(
              onPressed: () => controller.startOver(),
              child: const Text('Restart'),
            ),
          ),
        ],
      ),
    );
  }
}