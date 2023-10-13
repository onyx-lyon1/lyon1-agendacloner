import 'dart:convert';
import 'dart:developer';
import 'dart:io';
import 'package:encrypt/encrypt.dart';

void main(List<String> arguments) async {
  //generate key and iv
  if (!File("key.txt").existsSync()) {
    final key = Key.fromSecureRandom(256);
    File("key.txt").writeAsStringSync(key.base64);
  }
  if (!File("iv.txt").existsSync()) {
    final iv = IV.fromSecureRandom(16);
    File("iv.txt").writeAsStringSync(iv.base64);
  }

  //open data
  final plainText = File('agenda_ids.json').readAsStringSync();
  //compress data
  final enCodedJson = utf8.encode(plainText);
  final gZipJson = gzip.encode(enCodedJson);
  final base64Json = base64.encode(gZipJson);
  File("agenda_ids.json.compressed").writeAsStringSync(base64Json);

  //encrypt data
  final key = Key.fromBase64(File('key.txt').readAsStringSync());
  final iv = IV.fromBase64(File("iv.txt").readAsStringSync());
  File("iv.txt").writeAsStringSync(iv.base64);
  final encrypter = Encrypter(AES(key));
  final encrypted = encrypter.encrypt(base64Json, iv: iv);
  File("agenda_ids.json.enc").writeAsStringSync(encrypted.base64);
}
