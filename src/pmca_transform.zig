//! PMCA Transform list v2.0
//!
//! [name] 全身スケール
//! [range] 0.8 1.2
//! [scale] 1.0
//!
//! NEXT
//!
//! [name] 胴体
//! [range] 0.5 1.5
//! [ENTRY] 上半身
//! [length] 1.0
//! [ENTRY] 下半身
//! [length] 0.5
const std = @import("std");

const bom = [3]u8{
    0xEF, 0xBB, 0xBF,
};
const header = "PMCA Transform list v2.0";

const Entry = struct {
    name: []const u8,
    length: f32 = 0,
    thick: f32 = 0,
};

pub const Transform = struct {
    name: []const u8,
    // range: struct { f32, f32 },
    // scale: f32,
    entries: []Entry,
};

const Builder = struct {
    entries: std.ArrayList(Entry),
    name: []const u8 = "",
    current_entry: ?Entry = null,

    fn init(allocator: std.mem.Allocator) @This() {
        return .{
            .entries = std.ArrayList(Entry).init(allocator),
        };
    }

    fn deinit(self: @This()) void {
        self.entries.deinit();
    }

    fn commit(self: *@This()) !Transform {
        defer self.current_entry = null;
        defer self.name = "";
        return Transform{
            .name = self.name,
            .entries = try self.entries.toOwnedSlice(),
        };
    }

    fn isMatch(comptime prop: anytype, key: []const u8, value: []const u8) ?[]const u8 {
        if (std.mem.eql(u8, prop, key)) {
            return std.mem.trim(u8, value, &std.ascii.whitespace);
        } else {
            return null;
        }
    }

    pub fn set(self: *@This(), key: []const u8, _value: []const u8) !void {
        if (self.current_entry) |*entry| {
            if (isMatch("length", key, _value)) |value| {
                entry.length = try std.fmt.parseFloat(f32, value);
            } else if (isMatch("thick", key, _value)) |value| {
                entry.thick = try std.fmt.parseFloat(f32, value);
            } else if (isMatch("ENTRY", key, _value)) |value| {
                self.current_entry = Entry{
                    .name = value,
                };
            } else {
                std.debug.print("unkonwn entry key: {s}\n", .{key});
                @panic("unknown entry property");
            }
        } else {
            if (isMatch("name", key, _value)) |value| {
                self.name = value;
            } else if (isMatch("range", key, _value)) |value| {
                _ = value;
            } else if (isMatch("scale", key, _value)) |value| {
                _ = value;
            } else if (isMatch("default", key, _value)) |value| {
                _ = value;
            } else if (isMatch("pos", key, _value)) |value| {
                _ = value;
            } else if (isMatch("ENTRY", key, _value)) |value| {
                self.current_entry = Entry{
                    .name = value,
                };
            } else {
                std.debug.print("unkonwn transform key: {s}\n", .{key});
                @panic("unknown transform property");
            }
        }
    }
};

pub fn parse(allocator: std.mem.Allocator, _data: []const u8) ![]Transform {
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

    var list = std.ArrayList(Transform).init(allocator);
    var line_buf: [1024]u8 = undefined;
    var builder = Builder.init(allocator);
    defer builder.deinit();
    while (r.readUntilDelimiterOrEof(&line_buf, '\n')) |_line| {
        const line = _line orelse {
            // last
            if (builder.entries.items.len > 0) {
                try list.append(try builder.commit());
            }
            return list.toOwnedSlice();
        };
        // std.debug.print("{s}\n", .{line});

        const trimed = std.mem.trim(u8, line, &std.ascii.whitespace);
        if (trimed.len == 0) {
            continue;
        }

        if (std.mem.eql(u8, trimed, "NEXT")) {
            // commit
            try list.append(try builder.commit());
        } else if (trimed[0] == '[') {
            if (std.mem.indexOf(u8, trimed, "]")) |close| {
                try builder.set(trimed[1..close], trimed[close + 1 ..]);
            }
        } else {
            unreachable;
        }
    } else |_| {
        @panic("error");
    }

    return try list.toOwnedSlice();
}

