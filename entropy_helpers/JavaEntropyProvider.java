import java.io.FileDescriptor;
import java.io.FileOutputStream;
import java.io.IOException;

import java.nio.file.Files;
import java.nio.file.Paths;

import java.security.NoSuchAlgorithmException;
import java.security.ProviderException;
import java.security.SecureRandom;

import java.util.Arrays;


public final class JavaEntropyProvider {
    private static final int CONTRIBUTION_BYTES = 32;

    private static final int EXIT_GENERATION_FAILED = 10;
    private static final int EXIT_UNAVAILABLE = 11;
    private static final int EXIT_PROTOCOL = 12;

    private static final String EXPECTED_ALGORITHM =
        "NativePRNGBlocking";

    private static final String EXPECTED_PROVIDER =
        "SUN";

    private JavaEntropyProvider() {
    }

    private static boolean validRequest(String[] args) {
        return (
            args.length == 4
            && "--provider".equals(args[0])
            && "java_secure_random".equals(args[1])
            && "--bytes".equals(args[2])
            && "32".equals(args[3])
        );
    }

    private static boolean isPipe(int descriptor)
        throws IOException {

        String target = Files.readSymbolicLink(
            Paths.get(
                "/proc/self/fd/"
                + descriptor
            )
        ).toString();

        return target.startsWith("pipe:[");
    }

    private static int run(String[] args)
        throws Exception {

        if (!validRequest(args)) {
            return EXIT_PROTOCOL;
        }

        if (
            !isPipe(1)
            || !isPipe(2)
        ) {
            return EXIT_PROTOCOL;
        }

        SecureRandom random;

        try {
            random = SecureRandom.getInstanceStrong();

        } catch (NoSuchAlgorithmException exc) {
            return EXIT_UNAVAILABLE;

        } catch (ProviderException exc) {
            return EXIT_GENERATION_FAILED;
        }

        if (
            !EXPECTED_ALGORITHM.equals(
                random.getAlgorithm()
            )
            || !EXPECTED_PROVIDER.equals(
                random.getProvider().getName()
            )
        ) {
            return EXIT_PROTOCOL;
        }

        byte[] data = new byte[CONTRIBUTION_BYTES];

        try {
            try {
                random.nextBytes(data);

            } catch (ProviderException exc) {
                return EXIT_GENERATION_FAILED;

            } catch (RuntimeException exc) {
                return EXIT_PROTOCOL;
            }

            try (
                FileOutputStream output =
                    new FileOutputStream(
                        FileDescriptor.out
                    )
            ) {
                output.write(data);
                output.flush();

            } catch (IOException exc) {
                return EXIT_PROTOCOL;
            }

            return 0;

        } finally {
            Arrays.fill(
                data,
                (byte) 0
            );
        }
    }

    public static void main(String[] args) {
        int code;

        try {
            code = run(args);

        } catch (Exception exc) {
            code = EXIT_PROTOCOL;
        }

        System.exit(code);
    }
}
