"use strict";

const assert = require("node:assert/strict");

const helper = require(
    process.argv[2]
);

const args = [
    "--provider",
    "javascript_webcrypto",
    "--bytes",
    "32"
];


function fixture() {
    const state = {
        generated: 0,
        writes: 0,
        chunks: [],
        data: null,
        fallback: 0
    };

    const fsApi = {
        readlinkSync() {
            return "pipe:[test]";
        },

        writeSync(fd, data, offset, length) {
            state.writes++;

            state.chunks.push(
                Buffer.from(
                    data.subarray(
                        offset,
                        offset + length
                    )
                )
            );

            return length;
        }
    };

    const cryptoApi = {
        getFips() {
            return 0;
        },

        randomBytes() {
            state.fallback++;
            throw new Error("forbidden");
        },

        webcrypto: {
            getRandomValues(data) {
                state.generated++;
                state.data = data;
                data.fill(65);
                return data;
            }
        }
    };

    const runtime = {
        version: "v24.22.2",
        versions: {
            openssl: "3.5.9"
        },
        platform: "linux",
        arch: "x64",
        execArgv: []
    };

    return {
        state,
        fsApi,
        cryptoApi,
        runtime
    };
}


const checks = [
    function successAndClear() {
        const f = fixture();

        assert.equal(helper.run(args, f), 0);
        assert.equal(f.state.generated, 1);

        assert.equal(
            Buffer.concat(f.state.chunks).length,
            32
        );

        assert.ok(
            f.state.data.every(
                value => value === 0
            )
        );
    },

    function invalidArguments() {
        const invalidCases = [
            [],
            ["--help"],
            [
                "--provider",
                "python_os",
                "--bytes",
                "32"
            ],
            [...args, "extra"]
        ];

        for (const invalid of invalidCases) {
            const f = fixture();

            assert.equal(
                helper.run(invalid, f),
                12
            );

            assert.equal(
                f.state.generated,
                0
            );
        }
    },

    function profileChanges() {
        const changes = [
            f => {
                f.runtime.version = "v20.20.2";
            },
            f => {
                f.runtime.versions.openssl = "other";
            },
            f => {
                f.runtime.platform = "win32";
            },
            f => {
                f.runtime.arch = "arm64";
            },
            f => {
                f.runtime.execArgv = ["--test"];
            },
            f => {
                f.cryptoApi.getFips = () => 1;
            }
        ];

        for (const change of changes) {
            const f = fixture();
            change(f);

            assert.equal(
                helper.run(args, f),
                12
            );

            assert.equal(
                f.state.generated,
                0
            );
        }
    },

    function pipeGuard() {
        const f = fixture();

        f.fsApi.readlinkSync = () => "/dev/null";

        assert.equal(helper.run(args, f), 12);
        assert.equal(f.state.generated, 0);
    },

    function unavailableDoesNotFallback() {
        const f = fixture();

        f.cryptoApi.webcrypto = null;

        assert.equal(helper.run(args, f), 11);
        assert.equal(f.state.fallback, 0);
    },

    function operationFailure() {
        const f = fixture();

        f.cryptoApi.webcrypto.getRandomValues = () => {
            const error = new Error("test");
            error.name = "OperationError";
            throw error;
        };

        assert.equal(helper.run(args, f), 10);
        assert.equal(f.state.writes, 0);
    },

    function unexpectedGenerationError() {
        const f = fixture();

        f.cryptoApi.webcrypto.getRandomValues = () => {
            throw new Error("test");
        };

        assert.equal(helper.run(args, f), 12);
    },

    function wrongReturnReference() {
        const f = fixture();

        f.cryptoApi.webcrypto.getRandomValues =
            () => new Uint8Array(32);

        assert.equal(helper.run(args, f), 12);
    },

    function partialWrites() {
        const f = fixture();

        f.fsApi.writeSync = (
            fd,
            data,
            offset,
            length
        ) => {
            const count = Math.min(5, length);

            f.state.chunks.push(
                Buffer.from(
                    data.subarray(
                        offset,
                        offset + count
                    )
                )
            );

            return count;
        };

        assert.equal(helper.run(args, f), 0);

        assert.deepEqual(
            Buffer.concat(f.state.chunks),
            Buffer.alloc(32, 65)
        );
    },

    function writeFailureDoesNotRegenerate() {
        const f = fixture();

        f.fsApi.writeSync = () => {
            throw new Error("pipe failed");
        };

        assert.equal(helper.run(args, f), 12);
        assert.equal(f.state.generated, 1);
    },

    function invalidWriteCounts() {
        for (const count of [
            0,
            -1,
            NaN,
            1.5,
            33
        ]) {
            const f = fixture();

            f.fsApi.writeSync = () => count;

            assert.equal(
                helper.run(args, f),
                12
            );

            assert.equal(
                f.state.generated,
                1
            );
        }
    },

    function clearOnGenerationError() {
        const f = fixture();

        f.cryptoApi.webcrypto.getRandomValues =
            data => {
                f.state.data = data;
                data.fill(65);
                throw new Error("test");
            };

        assert.equal(helper.run(args, f), 12);

        assert.ok(
            f.state.data.every(
                value => value === 0
            )
        );
    },

    function missingFipsInterface() {
        const f = fixture();

        delete f.cryptoApi.getFips;

        assert.equal(helper.run(args, f), 11);
    },

    function zeroPatternNotFiltered() {
        const f = fixture();

        f.cryptoApi.webcrypto.getRandomValues =
            data => data;

        assert.equal(helper.run(args, f), 0);

        assert.deepEqual(
            Buffer.concat(f.state.chunks),
            Buffer.alloc(32)
        );
    }
];


for (const check of checks) {
    check();
}

process.stdout.write(
    JSON.stringify(
        {
            checks: checks.length,
            ok: true
        }
    ) + "\n"
);
