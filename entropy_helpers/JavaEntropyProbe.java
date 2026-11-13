import java.nio.charset.StandardCharsets;
import java.security.NoSuchAlgorithmException;
import java.security.SecureRandom;
import java.security.Security;

public final class JavaEntropyProbe {
    private JavaEntropyProbe() {
    }

    private static String quote(String value) {
        if (value == null) {
            value = "";
        }

        StringBuilder result = new StringBuilder();
        result.append('"');

        for (int i = 0; i < value.length(); i++) {
            char c = value.charAt(i);

            switch (c) {
                case '"':
                    result.append("\\\"");
                    break;

                case '\\':
                    result.append("\\\\");
                    break;

                case '\b':
                    result.append("\\b");
                    break;

                case '\f':
                    result.append("\\f");
                    break;

                case '\n':
                    result.append("\\n");
                    break;

                case '\r':
                    result.append("\\r");
                    break;

                case '\t':
                    result.append("\\t");
                    break;

                default:
                    if (c < 0x20) {
                        result.append(
                            String.format(
                                "\\u%04x",
                                (int) c
                            )
                        );
                    } else {
                        result.append(c);
                    }
            }
        }

        result.append('"');
        return result.toString();
    }

    private static void add(
        StringBuilder result,
        String key,
        String value
    ) {
        result.append(',');
        result.append(quote(key));
        result.append(':');
        result.append(quote(value));
    }

    public static void main(String[] args) {
        if (
            args.length != 1
            || !"--describe".equals(args[0])
        ) {
            System.exit(12);
            return;
        }

        try {
            SecureRandom random =
                SecureRandom.getInstanceStrong();

            StringBuilder result = new StringBuilder(
                "{\"inspection_version\":1"
            );

            add(
                result,
                "java_version",
                System.getProperty(
                    "java.version",
                    ""
                )
            );

            add(
                result,
                "runtime_version",
                System.getProperty(
                    "java.runtime.version",
                    ""
                )
            );

            add(
                result,
                "java_vendor",
                System.getProperty(
                    "java.vendor",
                    ""
                )
            );

            add(
                result,
                "java_home",
                System.getProperty(
                    "java.home",
                    ""
                )
            );

            add(
                result,
                "vm_name",
                System.getProperty(
                    "java.vm.name",
                    ""
                )
            );

            add(
                result,
                "strong_algorithms",
                Security.getProperty(
                    "securerandom.strongAlgorithms"
                )
            );

            add(
                result,
                "algorithm",
                random.getAlgorithm()
            );

            add(
                result,
                "provider",
                random.getProvider().getName()
            );

            result.append('}');

            byte[] output = (
                result.toString() + "\n"
            ).getBytes(StandardCharsets.UTF_8);

            System.out.write(output);
            System.out.flush();

        } catch (NoSuchAlgorithmException exc) {
            System.exit(11);

        } catch (Exception exc) {
            System.exit(12);
        }
    }
}
