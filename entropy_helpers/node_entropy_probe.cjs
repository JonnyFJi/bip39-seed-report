"use strict";

const fs = require("fs");


function nullableBoolean(value) {
    if (
        value === true
        || value === 1
        || value === "true"
        || value === "1"
    ) {
        return true;
    }

    if (
        value === false
        || value === 0
        || value === "false"
        || value === "0"
    ) {
        return false;
    }

    return null;
}


function main() {
    const args = process.argv.slice(2);

    if (
        args.length !== 1
        || args[0] !== "--describe"
    ) {
        return 12;
    }

    let crypto = null;

    try {
        crypto = require("crypto");
    } catch (error) {
        crypto = null;
    }

    const webcrypto = (
        crypto
        && crypto.webcrypto
    );

    const variables = (
        process.config
        && process.config.variables
    ) || {};

    const metadata = {
        inspection_version: 1,

        node_version: process.version,

        node_executable: process.execPath,

        platform: process.platform,

        architecture: process.arch,

        openssl_version: (
            process.versions.openssl
            || null
        ),

        crypto_module_available: (
            crypto !== null
        ),

        webcrypto_get_random_values: Boolean(
            webcrypto
            && typeof webcrypto.getRandomValues
                === "function"
        ),

        fips_mode: (
            crypto
            && typeof crypto.getFips === "function"
        ) ? crypto.getFips() : null,

        shared_openssl: nullableBoolean(
            variables.node_shared_openssl
        ),

        configured_openssl: nullableBoolean(
            variables.node_use_openssl
        ),

        exec_argv: process.execArgv
    };

    const output = Buffer.from(
        JSON.stringify(metadata) + "\n",
        "utf8"
    );

    let offset = 0;

    while (offset < output.length) {
        const written = fs.writeSync(
            1,
            output,
            offset,
            output.length - offset
        );

        if (written <= 0) {
            return 12;
        }

        offset += written;
    }

    return 0;
}


try {
    process.exitCode = main();
} catch (error) {
    process.exitCode = 12;
}
