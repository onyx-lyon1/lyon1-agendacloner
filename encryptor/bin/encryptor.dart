import 'dart:convert';
import 'dart:developer';
import 'dart:io';
import 'package:encrypt/encrypt.dart';

void main(List<String> arguments) async {
  //open data
  final plainText = File('agenda_ids.json').readAsStringSync();
  //compress data
  final enCodedJson = utf8.encode(plainText);
  final gZipJson = gzip.encode(enCodedJson);
  final base64Json = base64.encode(gZipJson);
  File("agenda_ids.json.compressed").writeAsStringSync(base64Json);

  //encrypt data
  final key = Key.fromBase64(File('key.txt').readAsStringSync());
  var iv = IV.fromLength(16);
  var encrypter = Encrypter(AES(key));
  var encrypted = encrypter.encrypt(base64Json, iv: iv);
  File("agenda_ids.json.enc").writeAsStringSync(encrypted.base64);
}
