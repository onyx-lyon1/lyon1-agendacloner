import 'dart:convert';
import 'dart:developer';
import 'dart:io';
// import 'package:encrypt/encrypt.dart';
import 'package:encrypt/encrypt.dart';

void main(List<String> arguments) async {
  //encrypt data
  final plainText = File('agenda_ids.json').readAsStringSync();
  final key = Key.fromBase64(File('key.txt').readAsStringSync());
  var iv = IV.fromLength(16);
  var encrypter = Encrypter(AES(key));
  var encrypted = encrypter.encrypt(plainText, iv: iv);
  File("agenda_ids.json.enc").writeAsStringSync(encrypted.base64);
  Stopwatch stopwatch = new Stopwatch()..start();
  var decrypted = encrypter.decrypt(encrypted, iv: iv);
  print('aesdecrypt() executed in ${stopwatch.elapsed}');

  //decrypt data
  // final encrypted = File('agenda_ids.json.enc').readAsStringSync();
  // final key = Key.fromBase64(File('key.txt').readAsStringSync());
  // final iv = IV.fromLength(16);
  // final encrypter = Encrypter(AES(key));
  // final decrypted = encrypter.decrypt(Encrypted.fromBase64(encrypted), iv: iv);
  // File('agenda_ids_decrypted.json').writeAsStringSync(decrypted);
}
