"use strict";

const EXPECTED_NODE_VERSION = "v24.22.2";
const EXPECTED_OPENSSL_VERSION = "3.5.9";
const CONTRIBUTION_BYTES = 32;


function validRequest(args) {
    return Array.isArray(args)
        && args.length === 4
        && args[0] === "--provider"
        && args[1] === "javascript_webcrypto"
        && args[2] === "--bytes"
        && args[3] === "32";
}


function run(args, dependencies) {
    let data = null;

    try {
        const {
            fsApi,
            cryptoApi,
            runtime
        } = dependencies;

        if (!validRequest(args)) {
            return 12;
        }

        if (
            runtime.version !== EXPECTED_NODE_VERSION
            || runtime.versions.openssl
                !== EXPECTED_OPENSSL_VERSION
            || runtime.platform !== "linux"
            || runtime.arch !== "x64"
            || !Array.isArray(runtime.execArgv)
            || runtime.execArgv.length !== 0
        ) {
            return 12;
        }

        for (const fd of [1, 2]) {
            const target = fsApi.readlinkSync(
                "/proc/self/fd/" + fd
            );

            if (
                typeof target !== "string"
                || !target.startsWith("pipe:[")
            ) {
                return 12;
            }
        }

        if (
            !cryptoApi
            || !cryptoApi.webcrypto
            || typeof cryptoApi.webcrypto.getRandomValues
                !== "function"
            || typeof cryptoApi.getFips !== "function"
        ) {
            return 11;
        }

        if (cryptoApi.getFips() !== 0) {
            return 12;
        }

        data = new Uint8Array(
            CONTRIBUTION_BYTES
        );

        let returned;

        try {
            returned =
                cryptoApi.webcrypto.getRandomValues(
                    data
                );

        } catch (error) {
            if (
                error
                && (
                    error.name === "OperationError"
                    || error.code
                        === "ERR_CRYPTO_OPERATION_FAILED"
                )
            ) {
                return 10;
            }

            return 12;
        }

        if (returned !== data) {
            return 12;
        }

        let offset = 0;

        while (offset < data.byteLength) {
            const written = fsApi.writeSync(
                1,
                data,
                offset,
                data.byteLength - offset
            );

            if (
                !Number.isInteger(written)
                || written <= 0
                || written > data.byteLength - offset
            ) {
                return 12;
            }

            offset += written;
        }

        return 0;

    } catch (error) {
        return 12;

    } finally {
        if (data !== null) {
            data.fill(0);
        }
    }
}


function main() {
    const fsApi = require("node:fs");

    let cryptoApi;

    try {
        cryptoApi = require("node:crypto");

    } catch (error) {
        if (
            error
            && (
                error.code
                    === "ERR_UNKNOWN_BUILTIN_MODULE"
                || error.code === "ERR_NO_CRYPTO"
            )
        ) {
            return 11;
        }

        return 12;
    }

    return run(
        process.argv.slice(2),
        {
            fsApi,
            cryptoApi,
            runtime: process
        }
    );
}


module.exports = Object.freeze(
    {
        run
    }
);


if (require.main === module) {
    try {
        process.exitCode = main();

    } catch (error) {
        process.exitCode = 12;
    }
}
