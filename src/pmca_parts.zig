const std = @import("std");

const header = "PMCA Parts list v2.0";
const setdir = "SETDIR ";
const bom = [3]u8{
    0xEF, 0xBB, 0xBF,
};

// SETDIR ./parts/
//
// [name] セーラー服上半身01(スカート,長袖)
// [comment] 普通の長袖セーラー服、縦リボン
// [type] root
// [path] ub_mt_slr001_l_sk.pmd
// [joint] head,hand,lb_sk,body_acce
// [pic] ub_mt_slr001_l_sk.png
//
// NEXT

const Parts = struct {
    dir: []const u8 = "",
    name: []const u8 = "",

    pub fn set(self: *@This(), key: []const u8, value: []const u8) void {
        if (std.mem.eql(u8, "name", key)) {
            self.name = std.mem.trim(u8, value, &std.ascii.whitespace);
        } else {
            std.debug.print("unkonwn key: {s}\n", .{key});
            unreachable;
        }
    }
};

const Parser = struct {};

pub fn parse(_data: []const u8) !void {
    var data = _data;

    if (std.mem.startsWith(u8, data, &bom)) {
        data = data[bom.len..];
    }

    if (!std.mem.startsWith(u8, data, header)) {
        return error.no_header;
    }
    data = data[header.len..];

    while (data[0] == '\r' or data[0] == '\n') : (data = data[1..]) {
        // skip crlf
    }

    var s = std.io.fixedBufferStream(data);
    const r = s.reader();

    var line_buf: [1024]u8 = undefined;
    var parts = Parts{};
    while (r.readUntilDelimiterOrEof(&line_buf, '\n')) |_line| {
        const line = _line orelse {
            // last
            std.debug.print("{}\n", .{parts});
            break;
        };

        const trimed = std.mem.trim(u8, line, &std.ascii.whitespace);
        if (trimed.len == 0) {
            continue;
        }

        if (std.mem.startsWith(u8, trimed, setdir)) {
            parts.dir = trimed[setdir.len..];
        } else if (std.mem.eql(u8, trimed, "NEXT")) {
            // parts
            std.debug.print("{}\n", .{parts});
            parts = .{ .dir = parts.dir };
        } else if (trimed[0] == '[') {
            if (std.mem.indexOf(u8, trimed, "]")) |close| {
                parts.set(trimed[1..close], trimed[close + 1 ..]);
            }
        } else {
            unreachable;
        }
    } else |_| {
        @panic("error");
    }
}
