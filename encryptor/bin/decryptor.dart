import 'dart:convert';
import 'dart:developer';
import 'dart:io';
import 'package:encrypt/encrypt.dart';

void main(List<String> arguments) async {
  //decrypt data
  final encrypted = File('agenda_ids.json.enc').readAsStringSync();
  final key = Key.fromBase64(File('key.txt').readAsStringSync());
  final iv = IV.fromBase64(File("iv.txt").readAsStringSync());
  final encrypter = Encrypter(AES(key));
  final decrypted = encrypter.decrypt(Encrypted.fromBase64(encrypted), iv: iv);
  final decoded = base64.decode(decrypted);
  final deziped = gzip.decode(decoded);
  File('agenda_ids_decrypted.json').writeAsBytesSync(deziped);
}
