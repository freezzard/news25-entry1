// news-image-20261125 entrypoint (Node 22, standard library only).
//
// The entry image lives beside this file as entry.png: a 1024x1024 digest of
// Wednesday 25 November 2026, drawn at build time by build_paint.py. This
// program copies it to /output/entry.png after checking, byte by byte, that
// it is a whole, well-formed PNG inside the competition limits. It reads no
// network, writes nothing but the one output file, and runs twice with the
// same bytes every time.
//
// Outside the grader's container, MAKEFUN_OUTPUT_DIR stands in for /output:
//   mkdir -p out && MAKEFUN_OUTPUT_DIR=out node main.ts

import { createHash } from "node:crypto";
import { mkdirSync, readFileSync, writeFileSync } from "node:fs";
import { dirname, join } from "node:path";
import { fileURLToPath } from "node:url";

type PngChunk = {
  kind: string;
  offset: number;
  dataStart: number;
  dataLength: number;
  storedCrc: number;
  computedCrc: number;
};

type PngCheck = {
  valid: boolean;
  reason: string;
  width: number;
  height: number;
  chunkCount: number;
  chunkKinds: string;
  byteCount: number;
  sha256: string;
};

type LoadResult = {
  bytes: Buffer | undefined;
  loadError: string;
};

type CopyOutcome = {
  copied: boolean;
  destination: string;
  check: PngCheck;
};

const EXPECTED_WIDTH = 1024;
const EXPECTED_HEIGHT = 1024;
const MAX_ENTRY_BYTES = 1048576;
const PNG_SIGNATURE: ReadonlyArray<number> = [0x89, 0x50, 0x4e, 0x47, 0x0d, 0x0a, 0x1a, 0x0a];
const CHUNK_HEADER_BYTES = 8;
const CHUNK_CRC_BYTES = 4;
const CHUNK_LENGTH_BYTES = 4;
const IHDR_DATA_BYTES = 13;
const IHDR_BIT_DEPTH_OFFSET = 8;
const IHDR_COLOR_TYPE_OFFSET = 9;
const EXPECTED_BIT_DEPTH = 8;
const COLOR_TYPE_RGB = 2;
const COLOR_TYPE_RGBA = 6;

const CRC_TABLE: ReadonlyArray<number> = buildCrcTable();

function buildCrcTable(): Array<number> {
  const table: Array<number> = [];
  for (let entryIndex = 0; entryIndex < 256; entryIndex += 1) {
    let entryValue = entryIndex;
    for (let bitIndex = 0; bitIndex < 8; bitIndex += 1) {
      const lowestBitSet = (entryValue & 1) !== 0;
      entryValue = lowestBitSet ? (entryValue >>> 1) ^ 0xedb88320 : entryValue >>> 1;
    }
    table.push(entryValue >>> 0);
  }
  return table;
}

function crc32Of(bytes: Buffer, start: number, end: number): number {
  let running = 0xffffffff;
  for (let byteIndex = start; byteIndex < end; byteIndex += 1) {
    const tableIndex = (running ^ bytes[byteIndex]) & 0xff;
    running = (running >>> 8) ^ CRC_TABLE[tableIndex];
  }
  return (running ^ 0xffffffff) >>> 0;
}

function sha256Of(bytes: Buffer): string {
  return createHash("sha256").update(bytes).digest("hex");
}

function readBigEndian32(bytes: Buffer, offset: number): number {
  const firstByte = bytes[offset] << 24;
  const secondByte = bytes[offset + 1] << 16;
  const thirdByte = bytes[offset + 2] << 8;
  const fourthByte = bytes[offset + 3];
  return (firstByte | secondByte | thirdByte | fourthByte) >>> 0;
}

function signatureMatches(bytes: Buffer): boolean {
  if (bytes.length < PNG_SIGNATURE.length) {
    return false;
  }
  let matchedCount = 0;
  for (let sigIndex = 0; sigIndex < PNG_SIGNATURE.length; sigIndex += 1) {
    if (bytes[sigIndex] === PNG_SIGNATURE[sigIndex]) {
      matchedCount += 1;
    }
  }
  return matchedCount === PNG_SIGNATURE.length;
}

function failureCheck(reason: string, bytes: Buffer): PngCheck {
  return {
    valid: false,
    reason: reason,
    width: 0,
    height: 0,
    chunkCount: 0,
    chunkKinds: "",
    byteCount: bytes.length,
    sha256: sha256Of(bytes),
  };
}

function summarizeKinds(chunks: Array<PngChunk>): string {
  const kinds: Array<string> = [];
  for (const chunkRecord of chunks) {
    kinds.push(chunkRecord.kind);
  }
  return kinds.join(",");
}

function parsePngChunks(bytes: Buffer): { chunks: Array<PngChunk>; failure: string } {
  const foundChunks: Array<PngChunk> = [];
  let failureNote = "";
  let readOffset = PNG_SIGNATURE.length;
  let seenImageEnd = false;
  while (readOffset + CHUNK_HEADER_BYTES <= bytes.length) {
    const dataLength = readBigEndian32(bytes, readOffset);
    const kindText = bytes.subarray(readOffset + CHUNK_LENGTH_BYTES, readOffset + CHUNK_HEADER_BYTES).toString("latin1");
    const dataStart = readOffset + CHUNK_HEADER_BYTES;
    const dataEnd = dataStart + dataLength;
    const crcStart = dataEnd;
    const crcEnd = crcStart + CHUNK_CRC_BYTES;
    if (crcEnd > bytes.length) {
      failureNote = "truncated chunk " + kindText;
      break;
    }
    const storedCrc = readBigEndian32(bytes, crcStart);
    const computedCrc = crc32Of(bytes, readOffset + CHUNK_LENGTH_BYTES, dataEnd);
    const chunkRecord: PngChunk = {
      kind: kindText,
      offset: readOffset,
      dataStart: dataStart,
      dataLength: dataLength,
      storedCrc: storedCrc,
      computedCrc: computedCrc,
    };
    foundChunks.push(chunkRecord);
    if (kindText === "IEND") {
      seenImageEnd = true;
      readOffset = crcEnd;
      break;
    }
    readOffset = crcEnd;
  }
  if (failureNote === "" && seenImageEnd === false) {
    failureNote = "missing IEND chunk";
  }
  if (failureNote === "" && readOffset !== bytes.length) {
    failureNote = "trailing bytes after IEND";
  }
  return { chunks: foundChunks, failure: failureNote };
}

function checkPng(bytes: Buffer): PngCheck {
  const digest = sha256Of(bytes);
  if (bytes.length === 0) {
    return {
      valid: false,
      reason: "empty file",
      width: 0,
      height: 0,
      chunkCount: 0,
      chunkKinds: "",
      byteCount: 0,
      sha256: digest,
    };
  }
  if (bytes.length > MAX_ENTRY_BYTES) {
    return failureCheck("file over 1 MiB", bytes);
  }
  if (signatureMatches(bytes) === false) {
    return failureCheck("bad PNG signature", bytes);
  }
  const parsed = parsePngChunks(bytes);
  if (parsed.failure !== "") {
    return failureCheck(parsed.failure, bytes);
  }
  const firstChunk = parsed.chunks[0];
  if (firstChunk === undefined || firstChunk.kind !== "IHDR" || firstChunk.dataLength !== IHDR_DATA_BYTES) {
    return failureCheck("first chunk is not a 13-byte IHDR", bytes);
  }
  const imageWidth = readBigEndian32(bytes, firstChunk.dataStart);
  const imageHeight = readBigEndian32(bytes, firstChunk.dataStart + 4);
  if (imageWidth !== EXPECTED_WIDTH || imageHeight !== EXPECTED_HEIGHT) {
    return failureCheck("image is not 1024x1024", bytes);
  }
  const bitDepth = bytes[firstChunk.dataStart + IHDR_BIT_DEPTH_OFFSET];
  const colorType = bytes[firstChunk.dataStart + IHDR_COLOR_TYPE_OFFSET];
  const colorSupported = colorType === COLOR_TYPE_RGB || colorType === COLOR_TYPE_RGBA;
  if (bitDepth !== EXPECTED_BIT_DEPTH || colorSupported === false) {
    return failureCheck("unsupported PNG pixel format", bytes);
  }
  let dataChunkCount = 0;
  let crcMismatch = "";
  for (const chunkRecord of parsed.chunks) {
    if (chunkRecord.kind === "IDAT") {
      dataChunkCount += 1;
    }
    if (chunkRecord.storedCrc !== chunkRecord.computedCrc) {
      crcMismatch = "CRC mismatch in chunk " + chunkRecord.kind;
    }
  }
  if (dataChunkCount === 0) {
    return failureCheck("no IDAT chunk", bytes);
  }
  if (crcMismatch !== "") {
    return failureCheck(crcMismatch, bytes);
  }
  return {
    valid: true,
    reason: "ok",
    width: imageWidth,
    height: imageHeight,
    chunkCount: parsed.chunks.length,
    chunkKinds: summarizeKinds(parsed.chunks),
    byteCount: bytes.length,
    sha256: digest,
  };
}

function resolveOutputDir(): string {
  const envDir = process.env.MAKEFUN_OUTPUT_DIR;
  const chosenDir = envDir !== undefined && envDir !== "" ? envDir : "/output";
  return chosenDir;
}

function loadEntry(sourcePath: string): LoadResult {
  let loadedBytes: Buffer | undefined = undefined;
  let loadError = "";
  try { loadedBytes = readFileSync(sourcePath); } catch (caughtError) {
    loadError = caughtError instanceof Error ? caughtError.message : String(caughtError);
  }
  return { bytes: loadedBytes, loadError: loadError };
}

function writeVerifiedCopy(sourceBytes: Buffer, destinationPath: string, outputDir: string): PngCheck {
  mkdirSync(outputDir, { recursive: true });
  writeFileSync(destinationPath, sourceBytes);
  const writtenCheck = checkPng(readFileSync(destinationPath));
  return writtenCheck;
}

function copyEntry(): CopyOutcome {
  const scriptDir = dirname(fileURLToPath(import.meta.url));
  const sourcePath = join(scriptDir, "entry.png");
  const outputDir = resolveOutputDir();
  const destinationPath = join(outputDir, "entry.png");
  const loaded = loadEntry(sourcePath);
  if (loaded.bytes === undefined) {
    const loadCheck: PngCheck = {
      valid: false,
      reason: "cannot read entry.png: " + loaded.loadError,
      width: 0,
      height: 0,
      chunkCount: 0,
      chunkKinds: "",
      byteCount: 0,
      sha256: "",
    };
    return { copied: false, destination: destinationPath, check: loadCheck };
  }
  const entryCheck = checkPng(loaded.bytes);
  if (entryCheck.valid === false) {
    return { copied: false, destination: destinationPath, check: entryCheck };
  }
  const writtenCheck = writeVerifiedCopy(loaded.bytes, destinationPath, outputDir);
  const bytesMatch = writtenCheck.sha256 === entryCheck.sha256;
  if (bytesMatch === false) {
    writtenCheck.valid = false;
    writtenCheck.reason = "written copy differs from source";
    return { copied: false, destination: destinationPath, check: writtenCheck };
  }
  return { copied: true, destination: destinationPath, check: entryCheck };
}

function describeCheck(check: PngCheck): Array<string> {
  const lines: Array<string> = [];
  lines.push("entry.png bytes: " + check.byteCount);
  lines.push("entry.png sha256: " + check.sha256);
  lines.push("entry.png size: " + check.width + "x" + check.height);
  lines.push("entry.png chunks: " + check.chunkCount + " (" + check.chunkKinds + ")");
  lines.push("entry.png check: " + check.reason);
  return lines;
}

function main(): void {
  const outcome = copyEntry();
  const reportLines = describeCheck(outcome.check);
  for (const reportLine of reportLines) {
    console.log(reportLine);
  }
  if (outcome.copied) {
    console.log("copied to " + outcome.destination);
    return;
  }
  console.error("entry copy refused: " + outcome.check.reason);
  process.exitCode = 1;
}

main();
